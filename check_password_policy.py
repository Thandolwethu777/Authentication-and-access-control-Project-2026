"""Run MariaDB password-policy checks using a fresh locked account with no grants."""
import secrets
from getpass import getpass

import mariadb

from db import connect_as


def verify(cursor):
    account = "'policy_" + secrets.token_hex(8) + "'@'localhost'"
    create = f"CREATE USER {account} IDENTIFIED BY ? ACCOUNT LOCK"
    alter = f"ALTER USER {account} IDENTIFIED BY ?"
    for label, candidate in (("length", "Aa1!"), ("digit", "OnlyLetters!"),
                             ("uppercase", "alllower123!"), ("lowercase", "ALLUPPER123!"),
                             ("symbol", "NoSymbol123")):
        try:
            cursor.execute(create, (candidate,))
        except mariadb.Error as error:
            if error.errno != 1819:
                raise RuntimeError(f"{label}: expected 1819, received {error.errno}") from None
        else:
            raise RuntimeError(f"{label}: policy accepted the candidate")
        print("PASS", label, 1819)
    first = "Aa1!" + secrets.token_urlsafe(24)
    second = "Bb2!" + secrets.token_urlsafe(24)
    cursor.execute(create, (first,))
    cursor.execute(alter, (second,))
    try:
        cursor.execute(alter, (first,))
    except mariadb.Error as error:
        if error.errno != 1396:
            raise RuntimeError(f"Unexpected reuse error {error.errno}") from None
        cursor.execute("SHOW WARNINGS")
        if not any(code == 1819 and "reus" in message.lower() for _,code,message in cursor):
            raise RuntimeError("ALTER USER failed without a reuse diagnostic")
    else:
        raise RuntimeError("Previously used password accepted")
    print("PASS reuse rejected, 1396 with diagnostic 1819. Locked test account:", account)


if __name__ == "__main__":
    user = input("Provisioning MariaDB username: ").strip()
    with connect_as(user, getpass("Provisioning password: ")) as connection, connection.cursor() as cursor:
        verify(cursor)
