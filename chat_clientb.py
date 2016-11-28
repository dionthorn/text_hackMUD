import socket
import sys
import os

SRV_IP = '127.0.0.1'        # Servers ip
SRV_PN = 20000              # Servers port
SRV_AD = (SRV_IP, SRV_PN)

while True:                 # Get clients port attempt choice
    CLI_PN = int(input('Enter port to attempt with\n'))
    # Must be between 0 and 2**16 and not server port if on same local network
    if 0 < CLI_PN < 2**16 and CLI_PN != SRV_PN:
        break
    else:
        print('Incorrect Port Value\n')
CLI_IP = '127.0.0.1'
CLI_AD = (CLI_IP, CLI_PN)   # Client IP Address and Port

# Create the ability to connect to the server
cliSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cliSock.bind(CLI_AD)

# Ask the server if it remembers you
cliSock.sendto(bytes('/?log', 'utf-8'), SRV_AD)

# Recieve response if the server recognizes you
data, addr = cliSock.recvfrom(1024)

if data.decode()[0:5] == 'truth':   # Means server recognizes you
    loggedIn = True
    userName = data.decode()[5::]
elif data.decode() == 'false':      # Means server does not recognize you
    loggedIn = False
elif data.decode() == 'termi':      # Means server is in controlled shut down
    print('Server in controlled shut down state.\nTemporiarily Unavaliable.')
    sys.exit()
else:                               # This shouldn't happen.
    print(data.decode())

# Special Case Server Controlled Shutdown
DOWN = False
while True: # Main Loop
    
    while not loggedIn: # Ensure Login status
        login = input('Please Login using \'username:pass\' format or type \'register username:pass\'\n')
        if login == 'exit':
            sys.exit()
        if login[0:10] == '/register ':
            try: # Attempt to register
                cliSock.sendto(bytes('/register {}'.format(login[10::]), 'utf-8'), SRV_AD)
            except:
                print('Error Invalid Input')
        else:
            try: # Attempt to login
                cliSock.sendto(bytes('/logon {}'.format(login), 'utf-8'), SRV_AD)
            except:
                print('Error Invalid Input')

        # Await server response
        data, addr = cliSock.recvfrom(1024)

        if data.decode()[0:5] == 'truth': # Login Successful
            print('Login or Register Successful')
            userName = data.decode()[5::]
            loggedIn = True
            break
        elif data.decode()[0:5] == 'false': # Invalid Login Info
            print('Invalid Login or Register')
        elif data.decode()[0:5] == 'termi': # Server admin shut down
            print('Server in controlled shut down state\nTemporiarily unavaliable.')
            sys.exit()
        else:
            # Shouldn't happen.
            print(data.decode())

    # Send User input to server
    Message = input('Enter a command {} or /help:\n'.format(userName))

    if Message[0:7] == '/logoff' and loggedIn:
        # Client side login attempt while logged in, will make client log off
        loggedIn = False
        cliSock.sendto(bytes('/logoff', 'utf-8'), SRV_AD)
    elif Message[0:5] == '/quit' and loggedIn:
        # Client side nice guy log off
        cliSock.sendto(bytes('/logoff', 'utf-8'), SRV_AD)
        print('Goodbye, Thanks For Playing!')
        sys.exit()
    elif Message[0:5] == '/chat':
        cliSock.sendto(bytes(Message, 'utf-8'), SRV_AD)
        data, addr = cliSock.recvfrom(1024)
        if data.decode()[0:5] == 'truth':
            chatLog = data.decode()[5::].split(':')
            os.system('cls')
            print(format('### BEGIN CHAT ###', '#^60'))
            for i,line in enumerate(chatLog):
                if i != len(chatLog)-1:
                    temp = line.split(';')
                    print(format('{} said:'.format(temp[0]), ' >20'), ' {}'.format(temp[1]))
            print(format('### END CHAT ###', '#^60'))
        elif data.decode()[0:5] == 'termi':
            # Server in controlled shutdown
            DOWN = True
            print('Server Controlled Shutdown')
            sys.exit()
        else:
            # Recieve Server messsage
            print(data.decode()[5::])
    elif Message[0:6] == '/clear':
        # ability to clear console in windows console.
        os.system('cls')
    elif Message [0:5] == '/help':
        if len(Message) == 6:
            print('Possible Commands are:\n/logoff, /quit, /chat, /clear')
            print("Use '/help /logoff' to see command specific help.")
            print('Otherwise commands are logged in chat.')
        elif Message[6::] == '/logoff':
            print('/logoff is the nice way to let the server know you are leaving.')
            print('It also will take your IP/Port off the system logs.')
        elif Message[6::] == '/quit':
            print('/quit will perform a /logoff and exit the program.')
        elif Message[6::] == '/chat':
            print('/chat will display chat logs.')
        elif Message[6::] == '/clear':
            print('/clear will clear windows console text.')
    else:
        loggedIn = True

        try:
            # Attempt to send user input
            cliSock.sendto(bytes(Message, 'utf-8'), SRV_AD)
            # Await server response
            data, addr = cliSock.recvfrom(1024)

            if data.decode()[0:5] == 'truth':
                # A non command code was sent and logged as chat
                pass
            elif data.decode()[0:5] == 'termi':
                # Server in controlled shutdown
                DOWN = True
                print('Server Controlled Shutdown')
                sys.exit()
            else:
                # Recieve Server messsage
                print(data.decode())
        except:
            # When controlled shutdown is in effect all clients are forced to exit.
            if DOWN:
                sys.exit()
            print('Error Invalid Input')
