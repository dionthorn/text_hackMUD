import socket
import sys
import os

UDP_IP_ADDRESS = '127.0.0.1' # Servers address
UDP_PORT_NO = 10000 # Servers port

while True: # Get clients port attempt choice
    YOUR_PORT = int(input('Enter port to attempt with\n'))
    if 0 < YOUR_PORT < 2**16 and YOUR_PORT != 10000:
        break
    else:
        print('Incorrect Port Value\n')

# Create the ability to connect to the server
clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSock.bind((UDP_IP_ADDRESS, YOUR_PORT))

# Ask the server if it knows you
clientSock.sendto(bytes('12706', 'utf-8'), (UDP_IP_ADDRESS, UDP_PORT_NO))

# Recieve response on if the server recognizes you
data, addr = clientSock.recvfrom(1024)

if data.decode()[0:5] == '11111': # Means server recognizes you
    LOGGED_IN = True
    user_name = data.decode()[5::]
elif data.decode() == '00000': # Means server does not recognize you
    LOGGED_IN = False
elif data.decode() == '00001': # Means server is in controlled shut down
    print('Server in controlled shut down state\nTemporiarily unavaliable.')
    sys.exit()
else: # This shouldn't happen.
    print(data.decode())

# Special Case Handle
DOWN = False

while True: # Main Loop
    
    while not LOGGED_IN: # Ensure Login status
        login = input('Please Login using \'username:pass\' format or type \'registerusername:pass\'\n')
        if login[0:8] == 'register':
            try: # Attempt to register
                clientSock.sendto(bytes('93612{}'.format(login[8::]), 'utf-8'), (UDP_IP_ADDRESS, UDP_PORT_NO))
            except:
                print('Error Invalid Input')
        else:
            try: # Attempt to login
                clientSock.sendto(bytes('70612{}'.format(login), 'utf-8'), (UDP_IP_ADDRESS, UDP_PORT_NO))
            except:
                print('Error Invalid Input')

        # Await server response
        data, addr = clientSock.recvfrom(1024)

        if data.decode()[0:5] == '11111': # Login Successful
            print('Login or Register Successful')
            user_name = data.decode()[5::]
            LOGGED_IN = True
            break
        elif data.decode()[0:5] == '00000': # Invalid Login Info
            print('Invalid Login or Register')
        elif data.decode()[0:5] == '00001': # Server admin shut down
            print('Server in controlled shut down state\nTemporiarily unavaliable.')
            sys.exit()
        else:
            # Shouldn't happen.
            print(data.decode())

    # Send User input to server
    Message = input('Enter a command {}:\n'.format(user_name))

    if Message[0:5].lower() in ['70612','loggo'] and LOGGED_IN:
        # Client side login attempt while logged in, will make client log off
        LOGGED_IN = False
    elif Message[0:5].lower() in ['00000','quit','exit'] and LOGGED_IN:
        # Client side nice guy log off
        clientSock.sendto(bytes('00000', 'utf-8'), (UDP_IP_ADDRESS, UDP_PORT_NO))
        print('Goodbye, Thanks For Playing!')
        sys.exit()
    elif Message[0:5].lower() == 'clear':
        # ability to clear console in windows console.
        os.system('cls')
    else:
        LOGGED_IN = True

        try:
            # Attempt to send user input
            clientSock.sendto(bytes(Message, 'utf-8'), (UDP_IP_ADDRESS, UDP_PORT_NO))
            # Await server response
            data, addr = clientSock.recvfrom(1024)

            if data.decode()[0:5] == '11111':
                # A non command code was sent and logged as server chat
                pass
            elif data.decode()[0:5] == '00001':
                # Server in controlled shutdown
                DOWN = True
                print('Server Controlled Shutdown')
                sys.exit()
            else:
                # Recieve Server messsage
                print(data.decode()[5::])
        except:
            # When controlled shutdown is in effect all clients are forced to exit.
            if DOWN:
                sys.exit()
            print('Error Invalid Input')
