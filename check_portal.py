"""Exercise normal Flask login, sessions and collection endpoints on the demo dataset."""
import getpass
import secrets
import unittest

from app import app
from db import prompt_backend_password

PASSWORDS = {}


class PortalChecks(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def login(self, name):
        result = self.client.post("/login", json={"username": name, "password": PASSWORDS[name]})
        self.assertEqual(result.status_code, 200)
        page = self.client.get(result.json["dashboard"])
        self.assertEqual(page.status_code, 200)
        self.assertIn(b'role-dashboard.js', page.data)
        page.close()

    def test_anonymous_and_login_validation(self):
        self.assertEqual(self.client.get("/admin/grades").status_code, 401)
        self.assertEqual(self.client.post("/login", json=[]).status_code, 400)
        result = self.client.post("/login", json={"username": "student1", "password": secrets.token_urlsafe()})
        self.assertEqual(result.status_code, 401)

    def test_students(self):
        for name, number, first, courses in (
            ("student1", "CU001", "Thando", {"CS101", "CS201"}),
            ("student2", "CU002", "Sarah", {"CS101"}),
        ):
            with self.subTest(name=name):
                self.login(name)
                self.assertEqual(self.client.get("/session-info").json["first_name"], first)
                self.assertEqual({r["course_code"] for r in self.client.get("/my-courses").json}, courses)
                for path in ("/my-grades", "/my-enrolments"):
                    result = self.client.get(path)
                    self.assertEqual({r["student_number"] for r in result.json}, {number})
                    self.assertEqual({r["course_code"] for r in result.json}, courses)
                self.assertTrue(self.client.get("/my-lecturers").json)
                self.assertEqual(self.client.get("/my-grades?student_id=99").status_code, 400)
                self.assertEqual(self.client.get("/students").status_code, 403)
                self.assertEqual(self.client.get("/admin/grades").status_code, 403)
                self.assertEqual(self.client.patch("/admin/grades/1", json={"grade": 75}).status_code, 403)
                previous = self.client.get_cookie("session").value
                self.assertEqual(self.client.post("/logout").status_code, 200)
                self.client.set_cookie("session", previous)
                self.assertEqual(self.client.get("/session-info").status_code, 401)

    def test_lecturer(self):
        self.login("lecturer1")
        self.assertEqual({r["course_code"] for r in self.client.get("/lecturer/courses").json}, {"CS101"})
        self.assertEqual({r["student_number"] for r in self.client.get("/lecturer/students").json}, {"CU001","CU002"})
        self.assertEqual({r["course_code"] for r in self.client.get("/lecturer/grades").json}, {"CS101"})
        self.assertEqual(self.client.get("/lecturer/courses?course_code=EC101").status_code, 400)
        self.assertEqual(self.client.patch("/admin/grades/1", json={"grade": 75}).status_code, 403)

    def test_administrator(self):
        self.login("admin1")
        for collection in ("students","lecturers","grades","enrolments","courses"):
            result = self.client.get("/admin/" + collection)
            self.assertEqual(result.status_code, 200)
            self.assertTrue(result.json)
        grade = self.client.get("/admin/grades").json[0]
        path = "/admin/grades/" + str(grade["grade_id"])
        for invalid in (-1, 101, "NaN", "12.345", None):
            self.assertEqual(self.client.patch(path, json={"grade": invalid}).status_code, 400)
        # Idempotent write for a quiet reproduction database.
        self.assertEqual(self.client.patch(path, json={"grade": grade["grade"]}).status_code, 200)


if __name__ == "__main__":
    prompt_backend_password()
    for username in ("student1","student2","lecturer1","admin1"):
        PASSWORDS[username] = getpass.getpass(f"Portal password for {username}: ")
    unittest.main(verbosity=2)
