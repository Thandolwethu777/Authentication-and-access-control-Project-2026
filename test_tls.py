from db import get_connection

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT @@port, CURRENT_USER()")
print("Server and user:", cursor.fetchall())


cursor.execute("SHOW SESSION STATUS LIKE 'Ssl_cipher'")
print("TLS cipher:", cursor.fetchall())

cursor.execute("SHOW SESSION STATUS LIKE 'Ssl_version'")
print("TLS version:", cursor.fetchall())

cursor.close()
conn.close()