"""Run fixed, no-row privilege assertions in separately authenticated sessions."""
import argparse
from getpass import getpass

import mariadb

from db import connect_as

READ_COURSES = "SELECT course_id FROM courses LIMIT 0"
READ_ACCOUNTS = "SELECT username FROM app_users LIMIT 0"
UPDATE_GRADE = "UPDATE grades SET grade=50 WHERE 1=0"
DELETE_GRADE = "DELETE FROM grades WHERE 1=0"
CASES = {
    "admin_role_test": ("admin_role", [(READ_COURSES, 0), (UPDATE_GRADE, 0),
                                      (READ_ACCOUNTS, 1142), (DELETE_GRADE, 1142)]),
    "deny_test": ("portal_demo_role", [(READ_COURSES, 0), (READ_ACCOUNTS, 1142)]),
    "student_deny_test": ("student_role", [(READ_COURSES, 0), (READ_ACCOUNTS, 1142),
                                          (UPDATE_GRADE, 1142), (DELETE_GRADE, 1142)]),
    "lecturer_deny_test": ("lecturer_role", [(READ_COURSES, 0), (UPDATE_GRADE, 0),
                                             (READ_ACCOUNTS, 1142), (DELETE_GRADE, 1142)]),
}


def audit_policy(cursor):
    cursor.execute("SHOW GRANTS FOR portal_demo_role")
    grants = [" ".join(row[0].lower().replace(chr(96), "").split()) for row in cursor]
    if not (any("grant select on constructor_security.* to" in line for line in grants)
            and any("deny select on constructor_security.app_users to" in line for line in grants)):
        raise RuntimeError("Missing schema GRANT or explicit table DENY in the auditor's grant listing")
    print("PASS policy audit: schema SELECT grant and app_users SELECT denial")


def check_account(user, password):
    role, cases = CASES[user]
    passed = True
    with connect_as(user, password) as connection, connection.cursor() as cursor:
        cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE()")
        if cursor.fetchone() != (user + "@localhost", role):
            raise RuntimeError("Wrong authenticated account or default role")
        for sql, expected in cases:
            actual = 0
            try:
                cursor.execute(sql)
                if cursor.description:
                    cursor.fetchall()
            except mariadb.Error as error:
                actual = error.errno
            ok = actual == expected
            print("PASS" if ok else "FAIL", user, role, sql, f"expected={expected} actual={actual}")
            passed &= ok
        connection.rollback()
    return passed


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--account", choices=CASES)
    parser.add_argument("--audit-policy", action="store_true", help="Also check grants using a separate auditor login")
    args = parser.parse_args()
    if args.audit_policy:
        auditor = input("Policy auditor username: ").strip()
        with connect_as(auditor, getpass("Auditor password: ")) as connection, connection.cursor() as cursor:
            audit_policy(cursor)
    ok = True
    for account in ([args.account] if args.account else CASES):
        try:
            ok &= check_account(account, getpass(f"MariaDB password for {account}: "))
        except (RuntimeError, mariadb.Error) as error:
            print("FAIL", account, "session or grant prerequisite", getattr(error, "errno", str(error)))
            ok = False
    raise SystemExit(0 if ok else 1)
