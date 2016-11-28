import sqlite3
import os
from random import randint as rand

db_filename = 'database.db'
schema_filename = 'schema.sql'

db_is_new = not os.path.exists(db_filename)

conn = sqlite3.connect(db_filename)

if db_is_new:
    print('Creating schema')
    f = open(schema_filename, 'rt')
    schema = f.read()
    conn.executescript(schema)
    print('Inserting Admin data and test user')
    conn.execute("""
    insert into reg_users (username, password, creation)
    values ('admin', 'root_password', '2016-11-26')
    """)
    conn.execute("""
    insert into reg_users (username, password, creation)
    values ('test_new_user', 'password1', '2016-11-26')
    """)
    conn.execute("""
    insert into user_info (uipa, ucre, ucpu, uram, uhdd, ussd, unet, ulog)
    values ('256:256:256', 9001, 33, 16, 512, 0, 512, '127.0.0.1:9999')
    """)
    while True:
        try:
            conn.execute("""
            insert into user_info (uipa, ucre, ucpu, uram, uhdd, ussd, unet, ulog)
            values ('{}:{}:{}', 9001, 33, 16, 512, 0, 512, '')
            """.format(rand(0,255),rand(0,255),rand(0,255)))
            break
        except:
            print('Failed creating with random ip...')
    conn.commit()
else:
    print('Database exists, assume schema does too.')

cursor = conn.cursor()

cursor.execute("""SELECT * FROM reg_users""")

for row in cursor.fetchall():
    print(row)

cursor.execute("""SELECT * FROM user_info""")

for row in cursor.fetchall():
    print(row)
    
conn.commit()
conn.close()
