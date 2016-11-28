import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("""SELECT * FROM reg_users""")
for row in cursor.fetchall():
    print(row)

cursor.execute("""SELECT * FROM user_info""")
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()
