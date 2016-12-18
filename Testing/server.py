import socket, sqlite3, os, sys, time
from random import randint as rand
from threading import Thread
from socketserver import ThreadingMixIn

DEBUG = False # If True will print raw exceptions instead of server formatted exceptions.
SRV_AD = (SRV_IP, SRV_PN) = '127.0.0.1', 5000 # The servers IP/Port all clients need this to connect.
BUFF = 1024
DB_PATH = 'database.db' # SQL database default path

if not os.path.exists(DB_PATH): # Auto fail if database doesn't exist.
    print(format('! INVALID DATABASE FILE !', ' ^60'))
    sys.exit()

class ClientThread(Thread): # Each client gets their own thread for easy OOP management.
    
    def __init__(self, ip, port, sock):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        self.name = ''
        # SQL
        conn = sqlite3.connect(DB_PATH)
        curs = conn.cursor()
        curs.execute("""SELECT username, llog FROM user_reg""") # If user ip/port is the same as last login than auto log in.
        for un, llog in curs.fetchall():
            if llog == '{}:{}'.format(self.ip, self.port):
                self.name = un
                print('{}:{} LOGGED IN AS {}'.format(self.ip, self.port, un))
                self.sock.send(bytes('/user {}'.format(un), 'utf-8'))
                break
        curs.close()
        conn.close()
        # END SQL
        print('---New Thread For      - {}:{}'.format(ip, str(port)))

    def run(self):
        
        while True: # Keep client until disconnect detected
            
            try:    # Always attempt to recieve data from client
                d = self.sock.recv(BUFF)
                d = d.decode()
                
                if d[0:5] == '/say ':
                    
                    if not self.name:
                        self.broadcast(d[5::], (self.ip, self.port))
                        print('{}:{} SAID {}'.format(self.ip, self.port, d[5::]))
                    else:
                        self.broadcast(d[5::], self.name)
                        print('{} SAID {}'.format(self.name, d[5::]))
                        
                elif d[0:7] == '/logon ' and len(d) > 7 and ':' in d:
                    
                    if not self.name: # If they already have a name then they are already logged on
                        un, pw = d[7::].split(':')
                        # SQL
                        conn = sqlite3.connect(DB_PATH)
                        curs = conn.cursor()
                        curs.execute("""SELECT username, password, llog FROM user_reg""") # Search if correct un/pw
                        for user, passw, llog in curs.fetchall():
                            if user == un:
                                if passw == pw: # Then Correct.
                                    self.name = un
                                    print('{}:{} LOGGED IN AS {}'.format(self.ip, self.port, un))
                                    self.sock.send(bytes('/user {}'.format(un), 'utf-8'))
                                    curs.execute("""UPDATE user_reg SET llog = ? WHERE username = ?""", ('{}:{}'.format(self.ip, self.port),un))
                                    conn.commit()
                                    break
                        curs.close()
                        conn.close()
                        # END SQL
                    else:
                        self.sock.send(bytes('/logon {} Already Logged On: ERROR'.format(self.name), 'utf-8'))

                elif d[0:10] == '/register ' and len(d) > 10 and ':' in d:
                    if not self.name: # Already logged on if you have a name
                        un, pw = d[10::].split(':')
                        is_new = True
                        # SQL
                        conn = sqlite3.connect(DB_PATH)
                        curs = conn.cursor()
                        curs.execute("""SELECT username FROM user_reg""")
                        for user, in curs.fetchall():
                            if user == un:
                                self.sock.send(bytes('/register {} Already Exists: ERROR'.format(un), 'utf-8'))
                                is_new = False
                        if is_new:
                            try:
                                y, m, d, *r = time.localtime(time.time())
                                stime = '{}-{}-{}'.format(y, m, d)
                                curs.execute("""insert into user_reg (username, password, creation, llog) values (?, ?, ?, ?)""", (str(un), str(pw), str(stime), '{}:{}'.format(self.ip, self.port)))
                                self.name = un
                                print('{}:{} REGISTERED AS {}'.format(self.ip, self.port, un))
                                self.sock.send(bytes('/user {}'.format(un), 'utf-8'))
                                conn.commit()
                            except Exception as e:
                                print(e)
                        curs.close()
                        conn.close()
                    else:
                        self.sock.send(bytes('/register {} Already Logged On: ERROR'.format(self.name), 'utf-8'))

                elif d[0:6] == '/ping ' and len(d) > 6:
                    un = d[6::]
                    found = False
                    for i,t in enumerate(threads):
                        if t.name == un:
                            t.sock.send(bytes('/ping You Have Been Pinged By: {}'.format(self.name), 'utf-8'))
                            found = True
                            break
                    if found:
                        self.sock.send(bytes('/ping {} Was Pinged: Is Online'.format(un), 'utf-8'))
                    else:
                        self.sock.send(bytes('/ping {} Was Pinged: Is Not Online'.format(un), 'utf-8'))
           
                else: # Not A Command
                    if not self.name:
                        print('{}:{} SENT_DATA {}'.format(self.ip, self.port, d))
                    else:
                        print('{} SENT_DATA {}'.format(self.name, d))
                        
            except Exception as e: # Something is very wrong. Or client disconnected.
                if DEBUG == True:
                    print(e)
                else:
                    print('{} Has Disconnected'.format((self.ip, self.port)))
                for i,t in enumerate(threads): # Remove disconnected client
                    if t == self:
                        del(threads[i])
                break

    def broadcast(self, msg, sender): # Ability for each client to broadcast via /say to all other connected clients.
        for client in threads:
            client.sock.send(bytes('{}{} Said: {}'.format('/say ', sender, msg), 'utf-8'))

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP/IP socket
tcpsock.bind(SRV_AD)
threads = []

os.system('cls')
print('Server Now Listening...')

while True: # Main Loop
    tcpsock.listen(5)
    (conn, (ip, port)) = tcpsock.accept() # Accept connections
    print('---Got Connection From - {}:{}'.format(ip, port))
    newthread = ClientThread(ip, port, conn) # And start their thread
    newthread.start()
    threads.append(newthread)

for t in threads:
    t.join()
