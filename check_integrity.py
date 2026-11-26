"""Verify integrity constraints on disposable INSERTs in a rolled-back transaction."""
from getpass import getpass

import mariadb

from db import connect_as


def check_integrity():
    user = input("Provisioning MariaDB username: ").strip()
    with connect_as(user, getpass("Provisioning password: ")) as connection, connection.cursor() as cursor:
        cursor.execute("SELECT @@port, CURRENT_USER()")
        print("Verified server and account", cursor.fetchone())
        cursor.execute("SELECT e.enrolment_id,e.student_id,e.course_id FROM enrolments e JOIN grades g USING(enrolment_id) LIMIT 1")
        enrolment, student, course = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM enrolments WHERE enrolment_id=-1")
        if cursor.fetchone()[0]:
            raise RuntimeError("Negative fixture ID already exists")
        probes = [
            ("duplicate registration", 1062, "INSERT INTO enrolments (student_id,course_id) VALUES (?,?)", (student,course)),
            ("second final grade", 1062, "INSERT INTO grades (enrolment_id,grade) VALUES (?,80)", (enrolment,)),
            ("missing enrolment", 1452, "INSERT INTO grades (enrolment_id,grade) VALUES (-1,80)", ()),
            ("out-of-range grade", 4025, "UPDATE grades SET grade=101 WHERE enrolment_id=?", (enrolment,)),
        ]
        try:
            for name, expected, sql, params in probes:
                try:
                    cursor.execute(sql, params)
                except mariadb.Error as error:
                    if error.errno != expected:
                        raise RuntimeError(f"{name}: expected {expected}, got {error.errno}") from None
                else:
                    raise RuntimeError(f"{name}: unexpectedly allowed")
                print("PASS", name, expected)
        finally:
            connection.rollback()


if __name__ == "__main__":
    check_integrity()
