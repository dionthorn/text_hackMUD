# Does nothing but accept broadcast messages.

SRV_AD = (SRV_IP, SRV_PN) = '127.0.0.1', 5000   # The Game Servers IP and Port Number
CLI_AD = (CLI_IP, CLI_PN) = '127.0.0.1', 4999   # Clients IP/Port
BUFF = 1024         # Buffer size
CHAT = []           # locally stored chat logs

import socket, time, sys, os, msvcrt
from threading import Thread

class Send(Thread):
    
    def __init__(self, sock):
        Thread.__init__(self) # Threaded,
        self.sock = sock      # TCP Socket Handeling

    def console_update(self):
        os.system('cls')
        
        if len(CHAT) >= 1:
            print(format('', '#^60'))
            
            for line in CHAT:
                sender, msg = line.split(':')
                print('{}: {}'.format(format(sender, ' <25'), msg))
                
            print(format('', '#^60'))
        
    def run(self):
        self.console_update()
        timer = time.time()
        
        while True:
            
            if time.time()-timer > 10: # Seconds Before Updating Console
                self.console_update()
                timer = time.time()
                
            if msvcrt.kbhit(): # Await keyboard input, then block updates until input
                usr_input = input('>')
                
                if usr_input[0:5] == '/exit':
                    print('\nThanks for Playing!')
                    break
                self.console_update()
                timer = time.time()
        sys.exit()

        
class Recv(Thread):
    
    def __init__(self, sock):
        Thread.__init__(self)
        self.sock = sock

    def run(self):
        
        while True:

            try:
                data = self.sock.recv(BUFF)
                
            except:
                print('Disconnected\n')
                break

            data = data.decode()

            if data[0:5] == '/say ':    # Chat Broadcasts
                CHAT.append(data[5::])

                if len(CHAT) > 100:      # Store Up to 100, can be increased or decreased
                    CHAT.pop(0)
        sys.exit()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(CLI_AD)
try:
    s.connect(SRV_AD)
except:
    print('Server Is Not Online')
    sys.exit()

recvthread = Recv(s)
recvthread.start()
sendthread = Send(s)
sendthread.start()
threads = [recvthread, sendthread]

for t in threads:
    t.join()
