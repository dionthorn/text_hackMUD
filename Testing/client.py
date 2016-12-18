# Run via Command Prompt on windows in the following format:
# client.py ip_address port_number
# ip_address must be your valid ip address either local or external network ex: 127.0.0.1
# port_number must be a base ten integer between 1024 and 2**16, port must be forwarded for non local access

import sys

if len(sys.argv) == 1:
    print('Invalid Command Line Input')
    print('USE: client.py ip_address port_number')
    sys.exit()
    
else:
    
    try:
        
        if 1024 < int(sys.argv[2]) < 2**16:
            pass
        
        else:
            print('Invalid Port Number Range:\n  Must be between 1025 and 2^16')
            sys.exit()
            
    except:
        print('Port Number Must Be Base 10')
        sys.exit()
        
    try:
        temp = sys.argv[1].split('.')
        
        if len(temp) != 4:
            print('Incorrect IP Address')
            sys.exit()

        for num in temp:
            
            try:
                
                if 0 <= int(num) <= 255:
                    pass
                else:
                    print('Invalid IP Address Range:\n  Must be between 0 and 255')
                    sys.exit()
                
            except:
                print('IP Address Must Be Base 10')
                sys.exit()
        
    except Exception as e:
        print(e)
        sys.exit()

SRV_AD = (SRV_IP, SRV_PN) = '127.0.0.1', 5000               # The Game Servers IP and Port Number
CLI_AD = (CLI_IP, CLI_PN) = sys.argv[1], int(sys.argv[2])   # Clients IP/Port
BUFF = 1024         # Buffer size
CHAT = []           # locally stored chat logs
LOCAL_NAME = ''     # Will be assigned when you /logon

import socket, time, os, msvcrt
from threading import Thread

class Send(Thread):
    
    def __init__(self, sock):
        Thread.__init__(self) # Threaded,
        self.sock = sock      # TCP Socket Handeling

    def console_update(self):
        global LOCAL_NAME
        os.system('cls')
        
        if len(CHAT) >= 1:
            print(format('', '#^60'))
            
            for line in CHAT:
                sender, msg = line.split(':')
                print('{}: {}'.format(format(sender, ' <25'), msg))
                
            print(format('', '#^60'))

        if LOCAL_NAME == '':
            print('Enter Command or /help')
            
        else:
            print('Enter Command {}, or /help'.format(LOCAL_NAME))

    def run(self):
        self.console_update()
        timer = time.time()
        
        while True:
            
            if time.time()-timer > 10: # Seconds Before Updating Console
                self.console_update()
                timer = time.time()
                
            if msvcrt.kbhit(): # Await keyboard input, then block updates until input
                usr_input = input('>')
                
                if usr_input[0:5] == '/exit' or usr_input[0:7] == '/logoff':
                    print('\nThanks for Playing!')
                    break
                elif usr_input[0:5] == '/help':
                    print('Use:/register {username}:{password}\n  To make a new account.')
                    print('Use:/logon {username}:{password}\n  To logon as existing account.')
                    print('Use:/say {msg}\n  To speak in Chat')
                    print('Use:/exit or /logoff\n  To exit the game.')
                    input('Press Enter To Continue')
                to_send = bytes('{}'.format(usr_input),
                                'utf-8')
                self.sock.send(to_send)
                self.console_update()
                timer = time.time()
        sys.exit()

        
class Recv(Thread):
    
    def __init__(self, sock):
        Thread.__init__(self)
        self.sock = sock

    def run(self):
        global LOCAL_NAME
        
        while True:

            try:
                data = self.sock.recv(BUFF)
                
            except:
                print('Disconnected\n')
                break

            data = data.decode()

            if data[0:5] == '/say ':    # Chat Broadcasts
                CHAT.append(data[5::])

                if len(CHAT) > 15:      # Store Up to 15, can be increased or decreased
                    CHAT.pop(0)
            elif data[0:7] == '/logon ': # Server is telling you logon errors
                CHAT.append(data[7::])
                
            elif data[0:6] == '/user ': # Server is telling you your username
                LOCAL_NAME = str(data[6::])

            elif data[0:6] == '/ping ': # Server is telling you ping results
                CHAT.append(data[6::])

            elif data[0:10] == '/register ': # Server is telling you register results
                CHAT.append(data[10::])
                
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
