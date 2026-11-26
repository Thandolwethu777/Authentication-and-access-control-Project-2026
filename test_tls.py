from db import get_connection, prompt_backend_password


def main():
    prompt_backend_password()
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute("SELECT @@port, CURRENT_USER(), CURRENT_ROLE()")
        print("Server port, account and role", cursor.fetchone())
        cursor.execute("SHOW SESSION STATUS WHERE Variable_name IN ('Ssl_version', 'Ssl_cipher')")
        status = dict(cursor.fetchall())
        if not all(status.get(k) for k in ("Ssl_version", "Ssl_cipher")):
            raise RuntimeError("Could not verify TLS on the application connection")
        print("PASS", status["Ssl_version"], status["Ssl_cipher"])


if __name__ == "__main__":
    main()
