import sqlite3

DB_PATH = 'database.db'

conn = sqlite3.connect(DB_PATH)

curs = conn.cursor()

curs.execute("""SELECT * FROM user_reg""")

for row in curs.fetchall():
    print(row)

conn.close()
