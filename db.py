
import os

import mariadb
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return mariadb.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        plugin_dir=os.environ["DB_PLUGIN_DIR"],
    )
