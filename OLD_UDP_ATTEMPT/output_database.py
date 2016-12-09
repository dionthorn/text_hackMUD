import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("""SELECT * FROM user_reg""")
for row in cursor.fetchall():
    print(row)

cursor.execute("""SELECT * FROM user_nfo""")
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()
