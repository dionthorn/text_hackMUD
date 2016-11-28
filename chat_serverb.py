import socket
import sqlite3
import os
import sys
import time
from random import randint as rand

UDP_IP = '127.0.0.1'
UDP_PN = 20000
SRV_AD = (UDP_IP, UDP_PN)
servSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
servSock.bind(SRV_AD)
DB_FILE = 'database.db'
chatLog = []

if not os.path.exists(DB_FILE):
    print(format('INVALID DATABASE FILE', ' ^60'))
    sys.exit()
else:
    conn = sqlite3.connect(DB_FILE)
    curs = conn.cursor()
    curs.execute("""SELECT * FROM USER_REG""")
    userReg = {}
    for row in curs.fetchall():
        userReg[row[1]] = row[2]
    loggedIn = {}
    conn.close

print('Server Now Listening.\n')

while True:

    data, addr = servSock.recvfrom(1024)

    if addr in loggedIn:
        print(format(
              'Data Recieved From {}:'.format(loggedIn[addr]),
              ' >50'),
              ' {}'.format(data.decode()))
    else:
        print(format(
              'Data Recieved From {}:'.format(addr),
              ' >50'),
              ' {}'.format(data.decode()))

    if data.decode()[0:5] in ["/?log", "/?LOG"]:
        if addr in loggedIn:
            servSock.sendto(bytes('truth{}'.format(loggedIn[addr]),
                                  'utf-8'),
                            addr)
            print(format('{} Returned As {}'.format(addr, loggedIn[addr]),
                         ' ^60'))
        else:
            re = False
            if len(userReg) > 0:
                conn = sqlite3.connect(DB_FILE)
                curs = conn.cursor()
                curs.execute("""SELECT * FROM user_nfo""")
                for row in curs.fetchall():
                    if row[8] != '':
                        nfo = row[8].split(':')
                        nfo[1] = int(nfo[1])
                        if tuple(nfo) == addr:
                            re = True
                            curs.execute("""SELECT uuid, username FROM user_reg""")
                            for line in curs.fetchall():
                                if line[0] == row[0]:
                                    loggedIn[addr] = line[1]
                                    break
                            break
            curs.close()
            conn.close()
            if re:
                servSock.sendto(bytes('truth{}'.format(loggedIn[addr]),
                                      'utf-8'),
                                addr)
                print(format('{} Returned As {}'.format(addr, loggedIn[addr]),
                             ' ^60'))
            else:
                print(format('{} Is Not Logged On'.format(addr), ' ^60'))
                servSock.sendto(bytes('false', 'utf-8'), addr)

    elif data.decode()[0:7] == "/logoff":
        if addr in loggedIn:
            print(format('Removing {}'.format(loggedIn[addr]), ' ^60'))
            conn = sqlite3.connect(DB_FILE)
            curs = conn.cursor()
            curs.execute("""SELECT uuid, username FROM user_reg""")
            uuid = 0
            for row in curs.fetchall():
                if row[1] == loggedIn[addr]:
                    uuid = row[0]
            curs.execute("""UPDATE user_nfo SET ulog = ? WHERE uuid = ?""",
                         ('', uuid))
            conn.commit()
            curs.close()
            conn.close()
            del(loggedIn[addr])

    elif data.decode()[0:10] == "/register ":
        if addr in loggedIn:
            print(format('Register Attempt: Already Logged In: {}'.format(loggedIn[addr]),
                         ' ^60'))
            servSock.sendto(bytes('false', 'utf-8'), addr)
        else:
            nfo = data.decode()[10::].split(':')
            if nfo[0] in userReg:
                print(format('Register Attempt: Already Registered: {}'.format(nfo[0]),
                             ' ^60'))
                servSock.sendto(bytes('false', 'utf-8'), addr)

            else:
                conn = sqlite3.connect(DB_FILE)
                curs = conn.cursor()
                ltime = time.localtime(time.time())
                stime = '{}-{}-{}'.format(ltime[0], ltime[1], ltime[2])
                conn.execute("""insert into user_reg (username, password, creation)
                             values (?, ?, ?)
                             """, (nfo[0], nfo[1], stime))
                while True:
                    try:
                        conn.execute("""
                        insert into user_nfo (uipa, ucre, ucpu, uram, uhdd, ussd, unet, ulog)
                        values ('{}:{}:{}', 100, 33, 16, 512, 0, 512, '')
                        """.format(rand(0,255),rand(0,255),rand(0,255)))
    
                        break
                    except:
                        pass
                conn.commit()
                curs.close()
                conn.close()
                for usr in loggedIn:
                    if loggedIn[usr] == nfo[0]:
                        conn = sqlite3.connect(DB_FILE)
                        curs = conn.cursor()
                        curs.execute("""SELECT uuid, username FROM user_reg""")
                        uuid = 0
                        for row in curs.fetchall():
                            if row[1] == nfo[0]:
                                uuid = row[0]
                                break
                        curs.execute("""UPDATE user_nfo SET ulog ? WHERE uuid = ?""",
                                     ('{}:{}'.format(addr[0], addr[1]),
                                      uuid))
                        conn.commit()
                        curs.close()
                        conn.close()
                        del(loggedIn[addr])
                        break
                loggedIn[addr] = nfo[0]
                servSock.sendto(bytes('truth{}'.format(loggedIn[addr]),
                                      'utf-8'), addr)
                print(format('Register Successful', ' ^60'))
                print(format('Currently Logged In:', ' ^60'))
                for usr in loggedIn:
                    print(format('{} Logged In As: {}'.format(usr, loggedIn[usr]),
                                 ' ^60'))
                conn = sqlite3.connect(DB_FILE)
                curs = conn.cursor()
                curs.execute("""SELECT uuid, username FROM user_reg""")
                check = []
                for row in curs.fetchall():
                    check.append(row)
                for a in check:
                    if nfo[0] in a:
                        uuid = a[0]
                curs.execute("""UPDATE user_nfo SET ulog = ? WHERE uuid = ?""",
                             ('{}:{}'.format(addr[0], addr[1]), uuid))
                conn.commit()
                if len(userReg) > 0:
                    curs.execute("""SELECT * FROM user_nfo""")
                    for row in curs.fetchall():
                        if row[8] == '':
                            print(format('uuid {}: No Login Info'.format(row[0]),
                                         ' ^60'))
                        else:
                            print(format('uuid {}: {}'.format(row[0], row[8]),
                                         ' ^60'))
                curs.close()
                conn.close()

    elif data.decode()[0:7] == "/logon ":
        nfo = data.decode()[7::].split(':')   
        if nfo[0] not in userReg:
            servSock.sendto(bytes('false', 'utf-8'), addr)
            print('!Invalid Login By: {}'.format(addr))
        else:
            if userReg[nfo[0]] == nfo[1]:
                for usr in loggedIn:
                    if loggedIn[usr] == nfo[0]:
                        conn = sqlite3.connect(DB_FILE)
                        curs = conn.cursor()
                        curs.execute("""SELECT uuid, username FROM user_reg""")
                        uuid = 0
                        for row in curs.fetchall():
                            if row[1] == nfo[0]:
                                uuid = row[0]
                        curs.execute("""UPDATE user_nfo SET ulog = ? WHERE uuid = ?""",
                                     ('', uuid))
                        conn.commit()
                        curs.close()
                        conn.close()
                        del(loggedIn[usr])
                        break
                loggedIn[addr] = nfo[0]
                servSock.sendto(bytes('truth{}'.format(loggedIn[addr]), 'utf-8'), addr)
                print(format('Login Successful', ' ^60'))
                print(format('Currently Logged In:', ' ^60'))
                for usr in loggedIn:
                    print(format('{} Logged In As: {}'.format(usr, loggedIn[usr]),
                                 ' ^60'))
                conn = sqlite3.connect(DB_FILE)
                curs = conn.cursor()
                curs.execute("""SELECT uuid, username FROM user_reg""")
                check = []
                for row in curs.fetchall():
                    check.append(row)
                for a in check:
                    if nfo[0] in a:
                        uuid = a[0]
                curs.execute("""UPDATE user_nfo SET ulog = ? WHERE uuid = ?""",
                             ('{}:{}'.format(addr[0], addr[1]), uuid))
                conn.commit()
                if len(userReg) > 0:
                    curs.execute("""SELECT * FROM user_nfo""")
                    for row in curs.fetchall():
                        if row[8] == '':
                            print(format('uuid {}: No Login Info'.format(row[0]),
                                         ' ^60'))
                        else:
                            print(format('uuid {}: {}'.format(row[0], row[8]),
                                         ' ^60'))
                curs.close()
                conn.close()
            else:
                servSock.sendto(bytes('false', 'utf-8'), addr)
                print('!Login Failed By: {}'.format(addr))

    elif data.decode()[0:7] == "/admin ":
        if len(data.decode()) == 7:
            servSock.sendto(bytes('truth', 'utf-8'), addr)
        elif addr in loggedIn:
            if loggedIn[addr] == 'admin':
                nfo = data.decode()[7::].split(':')
                if nfo[0] == '?log':
                    servSock.sendto(bytes('admin' + '{}'.format(list(loggedIn.values())), 'utf-8'),
                                    addr)
                    print(format('Sent Logged In List To Admin', ' ^60'))
                elif nfo[0] == '?data':
                    to_send = []
                    conn = sqlite3.connect('database.db')
                    curs = conn.cursor()
                    curs.execute("""SELECT uuid, username FROM user_reg""")
                    for row in curs.fetchall():
                        to_send.append(row)
                    curs.close()
                    conn.close()
                    servSock.sendto(bytes('admin' + '{}'.format(to_send), 'utf-8'), addr)
                    print(format('Sent Uuid/Username Info To Admin', ' ^60'))
                elif nfo[0] == 'shut':
                    if nfo[1] == 'down':
                        if nfo[2] == 'now':
                            servSock.sendto(bytes('termi', 'utf-8'), addr)
                            del(loggedIn[addr])
                            break
                else:
                    print(format('Invalid Admin Command', ' ^60'))
                    servSock.sendto(bytes('truth', 'utf-8'), addr)
            else:
                print(format('Non Admin Attempting Admin Controls: {}'.format(addr),
                             ' ^60'))
                servSock.sendto(bytes('truth', 'utf-8'), addr)
    elif data.decode()[0:5] == "/chat":
        print(format('Sending Chat Logs To {}'.format(loggedIn[addr]),
                     ' ^60'))
        temp = ''
        for line in chatLog:
            temp = '{}{}{}{}{}'.format(temp, line[0], ';', line[1], ':')
        servSock.sendto(bytes('truth{}'.format(temp), 'utf-8'), addr)

    elif addr in loggedIn:
        print(format('{} Said: {}'.format(loggedIn[addr], data.decode()),
                     ' ^60'))
        chatLog.append((loggedIn[addr], data.decode()))
        if len(chatLog) > 25:
            chatLog.pop(0)
        servSock.sendto(bytes('truth', 'utf-8'), addr)

while loggedIn:
    print(format('Serving Shut Down Until All Logged On Are Notified.', ' ^60'))
    data, addr = servSock.recvfrom(1024)
    servSock.sendto(bytes('termi', 'utf-8'), addr)
    if addr in loggedIn:
        del(loggedIn[addr])
    if loggedIn == {}:
        break
    
print(format('Server Has Terminated All Logged On', ' ^60'))          
