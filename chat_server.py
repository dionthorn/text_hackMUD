import socket
import sqlite3
import os
import sys
import time
from random import randint as rand

UDP_IP_ADDRESS = '127.0.0.1'    # Server address
UDP_PORT_NO = 20000             # Server port
            # Create the server's socket
serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Bind it to the address and port
serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))
            # The server's expected database name.
db_filename = 'database.db'
chat_log = []

# Check to ensure database exists.
if not os.path.exists(db_filename):
    print('Invalid Path for Database, Exiting.')
    sys.exit()
else:
    # Connect to Database.
    conn = sqlite3.connect(db_filename)
    # Create cursor for reading the database
    cursor = conn.cursor()
    # Point cursor at everything in reg_users
    cursor.execute("""SELECT * FROM reg_users""")
    # Prepare to fill reg_users info
    reg_users = {}
    for row in cursor.fetchall():
        # Add to the reg_users dictionary
        reg_users[row[1]] = row[2]
    # Setup empty logged_in dictionary
    logged_in = {}
    # Close the connection making no changes.
    conn.close()
    if len(reg_users) > 0: # Show uuid last login registry, could be disabled.
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM user_info""")
        for row in cursor.fetchall():
            if row[8] == '':
                print('uuid {}: no recent login info'.format(row[0]))
            else:
                print('uuid {}: {}'.format(row[0], row[8]))
    conn.close()

# Maybe find a way to thread this loop for multiple clients.
print('Main Loop Initiating.\n')

while True: # Main Loop
    
    data, addr = serverSock.recvfrom(1024) # Get data!
    
    if addr in logged_in: # If already logged in then accept
        print(format('Data from {}:'.format(logged_in[addr]), ' >35') + ' {}'.format(str(data.decode())))
    else:
        print(format('Data from {}:'.format(str(addr)), ' >35') + ' {}'.format(str(data.decode())))

    if data.decode()[0:5] == '12706': # Am I logged in or returning?
        if addr in logged_in:
            serverSock.sendto(bytes('11111{}'.format(logged_in[addr]), 'utf-8'), addr)
            print('{} returned as {}'.format(addr, logged_in[addr]))
        else:
            returning = False
            if len(reg_users) > 0:
                conn = sqlite3.connect(db_filename)
                cursor = conn.cursor()
                cursor.execute("""SELECT * FROM user_info""")
                for row in cursor.fetchall():
                    if row[8] == '':
                        print('uuid {}: no login info'.format(row[0]))
                    else:
                        info = row[8].split(':')
                        info[1] = int(info[1])
                        if tuple(info) == addr:
                            returning = True
                            cursor.execute("""SELECT uuid, username FROM reg_users""")
                            for s in cursor.fetchall():
                                if s[0] == row[0]:
                                    logged_in[addr] = s[1]
                                    break
                            break
            cursor.close()
            conn.close()
            if returning:
                serverSock.sendto(bytes('11111{}'.format(logged_in[addr]), 'utf-8'), addr)
                print('{} returned as {}'.format(addr, logged_in[addr]))
            else:
                print('{} is not currently logged on'.format(addr))
                serverSock.sendto(bytes('00000', 'utf-8'), addr)
            
    elif data.decode()[0:5] == '00000': # Nice guy log off!
        if addr in logged_in:
            print('removing {}'.format(logged_in[addr]))
            del(logged_in[addr])

    elif data.decode()[0:5] == '93612': # Register attempt
        if addr in logged_in:
            print('register attempt from already logged in user: {}'.format(logged_in[addr]))
            serverSock.sendto(bytes('00000', 'utf-8'), addr)
        else:
            attempt = data.decode()[5::].split(':')
            if attempt[0] in reg_users:
                print('register attempt from already registered in user: {}'.format(attempt[0]))
                serverSock.sendto(bytes('00000', 'utf-8'), addr)
            else:
                conn = sqlite3.connect(db_filename)
                cursor = conn.cursor()
                localtime = time.localtime(time.time())
                print(localtime[0], localtime[1], localtime[2])
                str_time = '{}-{}-{}'.format(localtime[0], localtime[1], localtime[2])
                conn.execute("""
                insert into reg_users (username, password, creation)
                values ('{}', '{}', '{}')
                """.format(attempt[0], attempt[1], str_time))
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
                cursor.close()
                conn.close()
                for k in logged_in:
                    if logged_in[k] == attempt[0]:
                        conn = sqlite3.connect(db_filename)
                        cursor = conn.cursor()
                        cursor.execute("""SELECT uuid, username FROM reg_users""")
                        target = 0
                        for row in cursor.fetchall():
                            print(row)
                            if row[1] == attempt[0]:
                                target = row[0]
                        print(target)
                        cursor.execute("""UPDATE user_info SET ulog = '' WHERE uuid = ?""", (target))
                        conn.commit()
                        conn.close()
                        cursor.close()
                        del(logged_in[k])
                        break
                logged_in[addr] = attempt[0]
                serverSock.sendto(bytes('11111{}'.format(logged_in[addr]), 'utf-8'), addr)
                print('Register Successful')
                print('Currently logged in:\n')
                for k in logged_in:
                    print(k, 'Logged in as', logged_in[k])
                conn = sqlite3.connect(db_filename)
                cursor = conn.cursor()
                cursor.execute("""SELECT uuid, username FROM reg_users""")
                check = []
                for row in cursor.fetchall():
                    check.append(row)
                cursor.execute("""SELECT uuid, ulog FROM user_info""")
                check2 = []
                for row in cursor.fetchall():
                    check2.append(row)
                for a in check:
                    if attempt[0] in a:
                        uuid = a[0]
                for b in check2:
                    if uuid in b:
                        print(uuid, b[0])
                a_address = addr[0]
                a_port = addr[1]
                cursor.execute("""UPDATE user_info SET ulog = ? WHERE uuid = ?""", ('{}:{}'.format(a_address, a_port), uuid))
                conn.commit()
                if len(reg_users) > 0:
                    cursor.execute("""SELECT * FROM user_info""")
                    for row in cursor.fetchall():
                        if row[8] == '':
                            print('uuid {}: no login info'.format(row[0]))
                        else:
                            print('uuid {}: {}'.format(row[0], row[8]))
                cursor.close()
                conn.close()
            
    elif data.decode()[0:5] == '70612': # Login
        attempt = data.decode()[5::].split(':')
        if attempt[0] not in reg_users:
            serverSock.sendto(bytes('00000', 'utf-8'), addr)
            print('Invalid Login')
        else:
            if reg_users[attempt[0]] == attempt[1]:
                for k in logged_in:
                    if logged_in[k] == attempt[0]:
                        conn = sqlite3.connect(db_filename)
                        cursor = conn.cursor()
                        cursor.execute("""SELECT uuid, username FROM reg_users""")
                        target = 0
                        for row in cursor.fetchall():
                            print(row)
                            if row[1] == attempt[0]:
                                target = row[0]
                        print(target)
                        cursor.execute("""UPDATE user_info SET ulog = '' WHERE uuid = ?""", (target))
                        conn.commit()
                        conn.close()
                        cursor.close()
                        del(logged_in[k])
                        break
                logged_in[addr] = attempt[0]
                serverSock.sendto(bytes('11111{}'.format(logged_in[addr]), 'utf-8'), addr)
                print('Login Successful')
                print('Currently logged in:\n')
                for k in logged_in:
                    print(k, 'Logged in as', logged_in[k])
                conn = sqlite3.connect(db_filename)
                cursor = conn.cursor()
                cursor.execute("""SELECT uuid, username FROM reg_users""")
                check = []
                for row in cursor.fetchall():
                    check.append(row)
                cursor.execute("""SELECT uuid, ulog FROM user_info""")
                check2 = []
                for row in cursor.fetchall():
                    check2.append(row)
                for a in check:
                    if attempt[0] in a:
                        uuid = a[0]
                for b in check2:
                    if uuid in b:
                        print(uuid, b[0])
                a_address = addr[0]
                a_port = addr[1]
                cursor.execute("""UPDATE user_info SET ulog = ? WHERE uuid = ?""", ('{}:{}'.format(a_address, a_port), uuid))
                conn.commit()
                if len(reg_users) > 0:
                    cursor.execute("""SELECT * FROM user_info""")
                    for row in cursor.fetchall():
                        if row[8] == '':
                            print('uuid {}: no login info'.format(row[0]))
                        else:
                            print('uuid {}: {}'.format(row[0], row[8]))
                cursor.close()
                conn.close()
            else:
                serverSock.sendto(bytes('00000', 'utf-8'), addr)
                print('LOGIN FAILED')
                
    elif data.decode()[0:5].lower() == 'admin': # Admin Tools
        if len(data.decode()) == 5:
            serverSock.sendto(bytes('11111', 'utf-8'), addr)
        elif addr in logged_in:
            if logged_in[addr] == 'admin':
                attempt = data.decode()[5::].split(':')
                if attempt[0] == 'logged_in':
                    serverSock.sendto(bytes('admin' + '{}'.format(list(logged_in.values())), 'utf-8'), addr)
                    print('Sent List to admin.')
                if attempt[0] == 'shut': # Force Down Safe
                    if attempt[1] == 'down':
                        if attempt[2] == 'now':
                            serverSock.sendto(bytes('00001', 'utf-8'), addr)
                            del(logged_in[addr])
                            break
            else:
                print('Non Admin Attempting Admin Controls: {}'.format(addr))
                serverSock.sendto(bytes('11111', 'utf-8'), addr)
                
    elif data.decode()[0:4].lower() == 'chat': # Chat
        print('Sending Chat Logs to {}'.format(logged_in[addr]))
        temp = ''
        for i in chat_log:
            temp = '{}{}{}{}{}'.format(temp, i[0], ';', i[1], ':')
        #print(temp)
        serverSock.sendto(bytes('11111{}'.format(temp), 'utf-8'), addr)

    elif addr in logged_in: # Not a special command so must be server chat.
        print('{} said: {}'.format(logged_in[addr], data.decode()))
        chat_log.append((logged_in[addr], data.decode()))
        if len(chat_log) > 15:
            chat_log.pop(0)
        #print(chat_log)
        serverSock.sendto(bytes('11111', 'utf-8'), addr)

while logged_in: # Tell everyone server is in controlled shut down.
    print('Serving Shut Down Until All Logged On Are Notified.')
    data, addr = serverSock.recvfrom(1024) # Await data!
    serverSock.sendto(bytes('00001', 'utf-8'), addr) # Send TERMINATE code
    if addr in logged_in:   # Await all who logged in to be notified could,
        del(logged_in[addr])# use a timer to close after n secs.
    if logged_in == {}:     # Once all logged in are gone then finished.
        break

print('Server has Terminated')
