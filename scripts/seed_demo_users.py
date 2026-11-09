"""Set local demo passwords for existing Flask portal accounts.

Run from project root: python scripts/seed_demo_users.py
Requires db.py, .env and werkzeug already configured for the Flask application.
Passwords are entered privately and never saved in source files.
"""
import getpass
import sys
from pathlib import Path

# Allow importing the existing project's db.py when launched from scripts/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv(Path(__file__).resolve().parents[1] / '.env')
from db import get_connection

USERS = ('student1', 'student2', 'lecturer1', 'admin1')


def main():
    print('Local demonstration account setup (Flask passwords, not MariaDB PARSEC).')
    print('This updates password hashes only; other account details stay unchanged.')
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT username FROM app_users WHERE username IN (?, ?, ?, ?) AND is_active = TRUE",
            USERS,
        )
        found = {row[0] for row in cursor.fetchall()}
        missing = set(USERS) - found
        if missing:
            raise RuntimeError('Missing active demo accounts: ' + ', '.join(sorted(missing)) + '. Run sample_data.sql first.')

        changes = []
        for username in USERS:
            while True:
                password = getpass.getpass(f'New demo password for {username}: ')
                confirm = getpass.getpass('Repeat password: ')
                if password != confirm:
                    print('Passwords do not match. Try again.')
                elif len(password) < 12:
                    print('Please use at least 12 characters.')
                else:
                    changes.append((generate_password_hash(password), username))
                    break
        for password_hash, username in changes:
            cursor.execute(
                'UPDATE app_users SET password_hash = ? WHERE username = ? AND is_active = TRUE',
                (password_hash, username),
            )
        connection.commit()
        print('Success: all four local demo password hashes have been saved.')
        print('Use each username and its chosen password to log in to Flask.')
    except Exception as exc:
        if connection is not None:
            connection.rollback()
        print(f'Setup failed: {exc}', file=sys.stderr)
        sys.exit(1)
    finally:
        if connection is not None:
            connection.close()


if __name__ == '__main__':
    main()
