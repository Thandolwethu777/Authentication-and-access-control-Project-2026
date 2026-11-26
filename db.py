"""Read non-secret settings from .env. Supply database secrets at runtime."""
import os
from getpass import getpass
from pathlib import Path

from dotenv import dotenv_values

_config = dotenv_values(Path(__file__).with_name(".env"), interpolate=False)


def setting(name, default=None):
    return os.environ.get(name, _config.get(name, default))


# Keep the handle alive while Connector/C loads authentication plugins.
_bin = Path(setting("MARIADB_BIN_DIR", r"C:\Program Files\MariaDB 13.1\bin"))
_dll_directory = os.add_dll_directory(str(_bin)) if os.name == "nt" and _bin.is_dir() else None

import mariadb


def connect_as(user, password):
    port = int(setting("DB_PORT", "3306"))
    options = dict(host=setting("DB_HOST", "127.0.0.1"), port=port,
                   user=user, password=password, database=setting("DB_NAME", "constructor_security"),
                   ssl=True, ssl_verify_cert=True, connect_timeout=5)
    for option, key in (("plugin_dir", "DB_PLUGIN_DIR"), ("ssl_ca", "DB_SSL_CA")):
        if setting(key):
            options[option] = setting(key)
    connection = mariadb.connect(**options)
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT @@port")
        if cursor.fetchone()[0] != port or not connection.tls_cipher:
            raise RuntimeError("Unexpected server port or unencrypted connection")
        cursor.close()
        return connection
    except BaseException:
        connection.close()
        raise


def get_connection():
    user = setting("DB_USER", "backend_user")
    if user != "backend_user":
        raise RuntimeError("Set DB_USER=backend_user and provision the PARSEC account first")
    return connect_as(user, os.environ["PORTAL_DB_PASSWORD"])


def prompt_backend_password():
    if "PORTAL_DB_PASSWORD" not in os.environ:
        os.environ["PORTAL_DB_PASSWORD"] = getpass(f"MariaDB password for {setting('DB_USER', 'backend_user')}: ")
