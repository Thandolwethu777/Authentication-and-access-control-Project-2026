import os
import secrets
from threading import Lock
from time import monotonic
from decimal import Decimal, InvalidOperation

import mariadb
from flask import Flask, abort, g, jsonify, redirect, request, send_from_directory, session
from werkzeug.security import check_password_hash

from db import get_connection, prompt_backend_password

app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_bytes(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
                  MAX_CONTENT_LENGTH=16 * 1024)

# The classroom deployment runs one Flask process. Restarting it ends all sessions.
SESSION_SECONDS = 8 * 60 * 60
active_sessions = {}
session_lock = Lock()


def start_session(user_id):
    now = monotonic()
    token = secrets.token_urlsafe(32)
    with session_lock:
        active_sessions.pop(session.get("token"), None)
        for expired in [key for key, until in active_sessions.items() if until <= now]:
            del active_sessions[expired]
        active_sessions[token] = now + SESSION_SECONDS
    session.clear()
    session.update(user_id=user_id, token=token)


PAGES = {"student": "dashboard.html", "lecturer": "lecturer-dashboard.html",
         "admin": "admin-dashboard.html"}
ASSETS = {"script.js", "role-dashboard.js", "style.css", "dashboard.css"}
PROFILE = """
    SELECT a.app_user_id AS user_id, a.username, a.email, a.user_role AS app_role,
           a.student_id, a.lecturer_id, COALESCE(s.first_name,l.first_name) AS first_name,
           COALESCE(s.last_name,l.last_name) AS last_name
    FROM app_users a LEFT JOIN students s ON a.student_id=s.student_id
    LEFT JOIN lecturers l ON a.lecturer_id=l.lecturer_id
    WHERE a.app_user_id=? AND a.is_active=TRUE
"""


def db():
    if "connection" not in g:
        g.connection = get_connection()
    return g.connection


@app.teardown_appcontext
def disconnect(_error):
    connection = g.pop("connection", None)
    if connection is not None:
        connection.close()


def rows(sql, params=()):
    with db().cursor(dictionary=True) as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()


def identity(role=None):
    with session_lock:
        active = active_sessions.get(session.get("token"), 0) > monotonic()
    if not active or "user_id" not in session:
        session.clear()
        abort(401)
    if "profile" not in g:
        result = rows(PROFILE, (session["user_id"],))
        if not result:
            session.clear()
            abort(401)
        g.profile = result[0]
    if role and g.profile["app_role"] != role:
        abort(403)
    return g.profile


@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
def api_error(error):
    return jsonify(error=error.description), error.code


@app.errorhandler(mariadb.Error)
def database_error(error):
    app.logger.error("Database request failed (MariaDB %s)", error.errno)
    return jsonify(error="Database request failed"), 503


@app.after_request
def private_response(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/")
def home():
    return send_from_directory(app.root_path, "index.html")


@app.get("/<filename>")
def frontend(filename):
    if filename in PAGES.values():
        if "user_id" not in session:
            return redirect("/")
        expected = PAGES[identity()["app_role"]]
        if filename != expected:
            return redirect("/" + expected)
    elif filename not in ASSETS:
        abort(404)
    return send_from_directory(app.root_path, filename)


@app.post("/login")
def login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        abort(400, "Send a JSON object")
    username, password = data.get("username"), data.get("password")
    if not isinstance(username, str) or not username.strip() or not isinstance(password, str) or not password:
        abort(400, "Username and password are required")
    result = rows("""SELECT app_user_id, username, user_role, password_hash FROM app_users
                     WHERE username=? AND is_active=TRUE""", (username.strip(),))
    if not result or not result[0]["password_hash"] or not check_password_hash(result[0]["password_hash"], password):
        abort(401, "Invalid username or password")
    account = result[0]
    start_session(account["app_user_id"])
    return jsonify(message="Login successful", dashboard="/" + PAGES[account["user_role"]],
                   user=dict(user_id=account["app_user_id"], username=account["username"], app_role=account["user_role"]))


@app.post("/logout")
def logout():
    with session_lock:
        active_sessions.pop(session.get("token"), None)
    session.clear()
    return jsonify(message="Logged out successfully")


@app.get("/account-info")
@app.get("/session-info")
def account_info():
    return jsonify(identity())


# Only server-owned SQL fragments enter these queries. IDs are bound values.
COURSES = "SELECT DISTINCT c.course_id,c.course_code,c.course_name FROM courses c"
STUDENTS = "SELECT DISTINCT s.student_id,s.student_number,s.first_name,s.last_name,s.email FROM students s"
LECTURERS = "SELECT DISTINCT l.lecturer_id,l.first_name,l.last_name,l.email,l.department FROM lecturers l"
REGISTRATION = """ FROM enrolments e JOIN students s ON s.student_id=e.student_id
                   JOIN courses c ON c.course_id=e.course_id"""
ENROLMENTS = "SELECT e.enrolment_id,s.student_number,c.course_code,c.course_name,e.enrolment_date" + REGISTRATION
GRADES = ("SELECT g.grade_id,s.student_number,c.course_code,c.course_name,g.grade" + REGISTRATION
          + " JOIN grades g ON g.enrolment_id=e.enrolment_id")
BY_STUDENT = " WHERE e.student_id=?"
ASSIGNED = " JOIN course_lecturers cl ON cl.course_id=c.course_id WHERE cl.lecturer_id=?"
ROSTERS = {
    "admin": {"students": STUDENTS, "lecturers": LECTURERS, "courses": COURSES,
              "enrolments": ENROLMENTS, "grades": GRADES},
    "student": {"courses": COURSES + " JOIN enrolments e ON e.course_id=c.course_id" + BY_STUDENT,
                "grades": GRADES + BY_STUDENT, "enrolments": ENROLMENTS + BY_STUDENT,
                "lecturers": LECTURERS + " JOIN course_lecturers cl ON cl.lecturer_id=l.lecturer_id"
                             + " JOIN enrolments e ON e.course_id=cl.course_id" + BY_STUDENT},
    "lecturer": {"courses": COURSES + ASSIGNED, "grades": GRADES + ASSIGNED,
                 "students": STUDENTS + " JOIN enrolments e ON e.student_id=s.student_id"
                             + " JOIN courses c ON c.course_id=e.course_id" + ASSIGNED},
}


@app.get("/my-<resource>", defaults={"role": "student"})
@app.get("/<any(lecturer,admin):role>/<resource>")
def records(role, resource):
    profile = identity(role)
    if request.args:
        abort(400, "This collection does not accept filters")
    sql = ROSTERS[role].get(resource)
    if sql is None:
        abort(404)
    params = () if role == "admin" else (profile[role + "_id"],)
    return jsonify(rows(sql + " ORDER BY 1", params))


@app.get("/students")
@app.get("/lecturers")
@app.get("/courses")
def administrative_collection():
    return records("admin", request.path[1:])


@app.patch("/admin/grades/<int:grade_id>")
def update_grade(grade_id):
    identity("admin")
    data = request.get_json(silent=True)
    try:
        if not isinstance(data, dict) or set(data) != {"grade"}:
            raise ValueError
        grade = Decimal(str(data["grade"]))
        if not grade.is_finite() or not 0 <= grade <= 100 or grade != grade.quantize(Decimal(".01")):
            raise ValueError
    except (InvalidOperation, ValueError):
        abort(400, "Grade must be a number from 0 to 100 with at most two decimal places")
    with db().cursor() as cursor:
        cursor.execute("SELECT grade_id FROM grades WHERE grade_id=? FOR UPDATE", (grade_id,))
        if cursor.fetchone() is None:
            abort(404, "Grade not found")
        cursor.execute("UPDATE grades SET grade=? WHERE grade_id=?", (grade, grade_id))
    db().commit()
    return jsonify(grade_id=grade_id, grade=grade)


if __name__ == "__main__":
    prompt_backend_password()
    app.run(host="127.0.0.1", port=int(os.environ.get("FLASK_PORT", "5000")))
