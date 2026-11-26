"""Provision new local SQL identities without writing their passwords to disk."""
from getpass import getpass

from db import connect_as
from test_deny import CASES, audit_policy


def provision():
    admin = input("MariaDB administrator username: ").strip()
    users = {"backend_user": "backend_role", **{user: pair[0] for user, pair in CASES.items()}}
    with connect_as(admin, getpass("Administrator password: ")) as conn, conn.cursor() as cur:
        cur.execute("SELECT @@port, VERSION()")
        print("Connected server", cur.fetchone())
        cur.execute("SELECT PLUGIN_STATUS FROM information_schema.PLUGINS WHERE PLUGIN_NAME='parsec'")
        if cur.fetchone() != ("ACTIVE",):
            raise SystemExit("Enable auth_parsec in the administrator session first.")
        audit_policy(cur)
        for name, role in users.items():
            cur.execute("SELECT plugin,ssl_type FROM mysql.user WHERE User=? AND Host='localhost'", (name,))
            old = cur.fetchone()
            plugin = "parsec" if name == "backend_user" else "mysql_native_password"
            if old:
                if old != (plugin, "ANY"):
                    raise SystemExit(f"Existing {name} has a different authentication or TLS policy. Review it privately.")
                print("Checking existing account", name)
            else:
                secret = getpass(f"Choose a strong private password for {name}: ")
                if not secret or secret != getpass("Repeat password: "):
                    raise SystemExit("Passwords must be nonempty and match")
                # Identifiers come exclusively from the fixed mapping above.
                cur.execute(f"CREATE USER '{name}'@'localhost' IDENTIFIED VIA {plugin} USING PASSWORD(?) REQUIRE SSL", (secret,))
            cur.execute(f"GRANT {role} TO '{name}'@'localhost'")
            cur.execute(f"SET DEFAULT ROLE {role} FOR '{name}'@'localhost'")
            print("Ready", name, role, plugin)


if __name__ == "__main__":
    provision()
