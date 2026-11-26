"""Compare the same account and endpoint with three MariaDB CLI TLS policies."""
import os
import re
import subprocess
from getpass import getpass
from pathlib import Path

from db import setting


def check_transport(user, password):
    client = Path(setting("MARIADB_BIN_DIR", r"C:\Program Files\MariaDB 13.1\bin")) / ("mariadb.exe" if os.name == "nt" else "mariadb")
    port = int(setting("DB_PORT", "3306"))
    base = [str(client), "--no-defaults", "--protocol=tcp", "--host=" + setting("DB_HOST", "127.0.0.1"),
            f"--port={port}", "--user=" + user, "--batch", "--skip-column-names"]
    if setting("DB_PLUGIN_DIR"):
        base.append("--plugin-dir=" + setting("DB_PLUGIN_DIR"))
    verified = ["--ssl", "--ssl-verify-server-cert"]
    if setting("DB_SSL_CA"):
        verified.append("--ssl-ca=" + setting("DB_SSL_CA"))
    checks = [("verified TLS", verified, 0), ("plaintext", ["--skip-ssl"], 1045),
              ("wrong certificate fingerprint", verified + ["--ssl-fp=" + "00" * 32], 2026)]
    for label, options, expected in checks:
        result = subprocess.run(base + options + ["-e", "SELECT @@port; SHOW SESSION STATUS LIKE 'Ssl_cipher'"],
                                env={**os.environ, "MYSQL_PWD": password}, capture_output=True, text=True)
        error = re.search(r"ERROR (\d+)", result.stderr)
        actual = int(error[1]) if error else (0 if result.returncode == 0 else -1)
        if actual != expected:
            raise RuntimeError(f"{label}: expected {expected}, received {actual}")
        if not expected and not re.fullmatch(rf"{port}\s+Ssl_cipher\s+\S+\s*", result.stdout):
            raise RuntimeError("Port or TLS cipher missing from positive control")
        print("PASS", user, label, "code", actual)


if __name__ == "__main__":
    user = setting("DB_USER", "backend_user")
    check_transport(user, getpass(f"MariaDB password for {user}: "))
