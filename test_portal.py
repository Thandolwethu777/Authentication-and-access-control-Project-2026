"""Offline Flask regressions. SQLite provides fixture rows, not MariaDB privilege or TLS evidence."""
import secrets
import sqlite3
import unittest
from pathlib import Path
from unittest.mock import patch

from werkzeug.security import generate_password_hash

import check_portal
from app import app


class FixtureCursor(sqlite3.Cursor):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def execute(self, sql, params=()):
        import decimal
        params = tuple(str(v) if isinstance(v, decimal.Decimal) else v for v in params)
        return super().execute(sql.removesuffix(" FOR UPDATE"), params)


class FixtureConnection(sqlite3.Connection):
    def cursor(self, dictionary=False):
        cursor = super().cursor(factory=FixtureCursor)
        if dictionary:
            cursor.row_factory = lambda cur, row: dict(zip((c[0] for c in cur.description), row))
        return cursor


class OfflinePortal(check_portal.PortalChecks):
    @classmethod
    def setUpClass(cls):
        name = "file:portal-fixture?mode=memory&cache=shared"
        def connect():
            return sqlite3.connect(name, uri=True, factory=FixtureConnection)
        mock = patch("app.get_connection", connect)
        mock.start()
        cls.addClassCleanup(mock.stop)
        connection = connect()
        with connection:
            for table, cols in {
                "students":"student_id,student_number,first_name,last_name,email",
                "lecturers":"lecturer_id,first_name,last_name,email,department",
                "courses":"course_id,course_code,course_name",
                "enrolments":"enrolment_id,student_id,course_id,enrolment_date",
                "grades":"grade_id,enrolment_id,grade",
                "app_users":"app_user_id,username,email,user_role,student_id,lecturer_id,password_hash,is_active",
            }.items():
                key, rest = cols.split(",",1)
                connection.execute(f"CREATE TABLE {table} ({key} INTEGER PRIMARY KEY,{rest})")
            connection.execute("CREATE TABLE course_lecturers (course_id,lecturer_id)")
            data = Path(__file__).with_name("sample_data.sql").read_text(encoding="utf-8-sig")
            connection.executescript(data.replace("USE constructor_security;", "").replace("INSERT IGNORE", "INSERT OR IGNORE"))
            for name_ in ("student1","student2","lecturer1","admin1"):
                password = secrets.token_urlsafe()
                check_portal.PASSWORDS[name_] = password
                connection.execute("UPDATE app_users SET password_hash=?,is_active=1 WHERE username=?",
                                   (generate_password_hash(password),name_))
            connection.execute("INSERT INTO app_users (username,user_role,password_hash,is_active) SELECT 'inactive',user_role,password_hash,0 FROM app_users WHERE username='student1'")
        cls.addClassCleanup(connection.close)

    def test_inactive(self):
        result = self.client.post("/login",json={"username":"inactive","password":check_portal.PASSWORDS["student1"]})
        self.assertEqual(result.status_code, 401)


if __name__ == "__main__":
    unittest.main(verbosity=2)
