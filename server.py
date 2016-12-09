import socket, sqlite3, os, sys, time
from random import randint as rand
from threading import Thread
from socketserver import ThreadingMixIn

DEBUG = True
SRV_AD = (SRV_IP, SRV_PN) = '127.0.0.1', 5000
BUFF = 1024
DB_PATH = 'database.db'

if not os.path.exists(DB_PATH):
    print(format('! INVALID DATABASE FILE !', ' ^60'))
    sys.exit()

class ClientThread(Thread):
    
    def __init__(self, ip, port, sock):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        # SQL
        conn = sqlite3.connect(DB_PATH)
        curs = conn.cursor()
        curs.execute("""SELECT username, llog FROM user_reg""")
        for un, llog in curs.fetchall():
            if llog == '':
                self.name = ''
            elif llog == '{}:{}'.format(self.ip, self.port):
                self.name = un
                print(un)
                break
        curs.close()
        conn.close()
        # END SQL
        print('New Thread For      - {}:{}'.format(ip, str(port)))

    def run(self):
        
        while True:
            
            try:
                d = self.sock.recv(BUFF)
                d = d.decode()
                
                if d[0:5] == '/say ':
                    
                    if not self.name:
                        self.broadcast(d[5::], (self.ip, self.port))
                        print('{}:{} SAID {}'.format(self.ip, self.port, d[5::]))
                    else:
                        self.broadcast(d[5::], self.name)
                        print('{} SAID {}'.format(self.name, d[5::]))
                        
                elif d[0:7] == '/logon ' and len(d) > 5 and ':' in d:
                    
                    if not self.name:
                        un, pw = d[7::].split(':')
                        # SQL
                        conn = sqlite3.connect(DB_PATH)
                        curs = conn.cursor()
                        curs.execute("""SELECT username, password, llog FROM user_reg""")
                        for user, passw, llog in curs.fetchall():
                            if user == un:
                                if passw == pw: # Then Correct.
                                    self.name = un
                                    print('{}:{} LOGGED IN AS {}'.format(self.ip, self.port, un))
                                    self.sock.send(bytes('/user {}'.format(un), 'utf-8'))
                                    curs.execute("""UPDATE user_reg SET llog = ? WHERE username = ?""", ('{}:{}'.format(self.ip, self.port),un))
                                    conn.commit()
                                    break
                            else:
                                break
                        
                        curs.close()
                        conn.close()
                        # END SQL
                    else:
                        print('{} ALREADY LOGGED ON'.format(self.name))
                        
                else: # Not A Command
                    if not self.name:
                        print('{}:{} SENT {}'.format(self.ip, self.port, d))
                    else:
                        print('{} SENT {}'.format(self.name, d))
                        
            except Exception as e: # Something is very wrong.
                if DEBUG == True:
                    print(e)
                else:
                    print('{} Has Disconnected'.format((self.ip, self.port)))
                for i,t in enumerate(threads):
                    if t == self:
                        del(threads[i])
                break

    def broadcast(self, msg, sender):
        for client in threads:
            client.sock.send(bytes('{}{} Said: {}'.format('/say ', sender, msg), 'utf-8'))

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.bind(SRV_AD)
threads = []

os.system('cls')
print('Server Now Listening...')

while True:
    tcpsock.listen(5)
    (conn, (ip, port)) = tcpsock.accept()
    print('Got Connection From - {}:{}'.format(ip, port))
    newthread = ClientThread(ip, port, conn)
    newthread.start()
    threads.append(newthread)

for t in threads:
    t.join()

