import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory, session, redirect
from db import get_connection
from werkzeug.security import check_password_hash

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ["FLASK_SECRET_KEY"]


@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/script.js")
def frontend_script():
    return send_from_directory(".", "script.js")

@app.route("/dashboard.js")
def serve_dashboard_script():
    return send_from_directory(".", "dashboard.js")

@app.route("/dashboard.html")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    
    return send_from_directory(".", "dashboard.html")

@app.route("/students", methods=["GET"])
def students():
    if "user_id" not in session:
        return jsonify({"error": "Please log in first"}), 401
    
    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT student_id, student_number, first_name, last_name, email
            FROM students
        """)

        rows = cursor.fetchall()

        students_list = []

        for row in rows:
            student = {
                "student_id": row[0],
                "student_number": row[1],
                "first_name": row[2],
                "last_name": row[3],
                "email": row[4],
            }

            students_list.append(student)

        return jsonify(students_list)

    except Exception:
        app.logger.exception("Failed to retrieve students")
        return jsonify({"error": "Could not retrieve students"}), 500

    finally:
        if connection is not None:
            connection.close()


@app.route("/courses", methods=["GET"])
def courses():
    if "user_id" not in session:
            return jsonify({"error": "Please log in first"}), 401
        
    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT course_id, course_code, course_name
            FROM courses
        """)

        rows = cursor.fetchall()

        courses_list = []

        for row in rows:
            course = {
                "course_id": row[0],
                "course_code": row[1],
                "course_name": row[2],
            }

            courses_list.append(course)

        return jsonify(courses_list)

    except Exception:
        app.logger.exception("Failed to retrieve courses")
        return jsonify({"error": "Could not retrieve courses"}), 500

    finally:
        if connection is not None:
            connection.close()

@app.route("/lecturers", methods=["GET"])
def lecturers():
    if "user_id" not in session:
        return jsonify({"error": "Please log in first"}), 401
            
    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT lecturer_id, first_name, last_name, email, department
            FROM lecturers
        """)

        rows = cursor.fetchall()

        lecturers_list = []

        for row in rows:
            lecturer = {
                "lecturer_id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "department": row[4],
            }

            lecturers_list.append(lecturer)

        return jsonify(lecturers_list)

    except Exception:
        app.logger.exception("Failed to retrieve lecturers")
        return jsonify({"error": "Could not retrieve lecturers"}), 500

    finally:
        if connection is not None:
            connection.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Send a JSON request body"}), 400

    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"error": "Username and password are required"}), 400

    username = username.strip()

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT user_id, username, password_hash, app_role
            FROM app_users
            WHERE username = ? AND is_active = TRUE
            """,
            (username,),
        )

        user = cursor.fetchone()

        if user is None or not check_password_hash(user[2], password):
            return jsonify({"error": "Invalid username or password"}), 401
        session.clear()
        session["user_id"] = user[0]
        session["username"] = user[1]
        session["app_role"] = user[3]

        return jsonify({
            "message": "Login successful",
            "user": {
                "user_id": user[0],
                "username": user[1],
                "app_role": user[3],
            },
        }), 200

    except Exception:
        app.logger.exception("Login failed due to a server error")
        return jsonify({"error": "An internal server error occurred"}), 500

    finally:
        if connection is not None:
            connection.close()

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)