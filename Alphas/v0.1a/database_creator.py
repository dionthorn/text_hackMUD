import sqlite3, os
from random import randint as rand

DB_PATH = 'database.db'
SCHEMA_PATH = 'schema.txt'

DB_IS_NEW = not os.path.exists(DB_PATH)

conn = sqlite3.connect(DB_PATH)

if DB_IS_NEW:
    print('Creating Schema')
    f = open(SCHEMA_PATH, 'rt')
    schema = f.read()
    conn.executescript(schema)
    print('Inserting Admin data and test user')
    conn.execute("""
    insert into user_reg (username, password, creation, llog)
    values ('admin', 'root_password', '2016-11-26', '')
    """)
    conn.execute("""
    insert into user_reg (username, password, creation, llog)
    values ('test_user', 'test_password', '2016-12-26', '')
    """)
    conn.commit()
else:
    print('Database exists, assume schema already applies.')

curs = conn.cursor()

curs.execute("""SELECT * FROM user_reg""")

for row in curs.fetchall():
    print(row)

conn.commit()
conn.close()
