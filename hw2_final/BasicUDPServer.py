# Submitter :
# Jesoon Kang, 20170937
# Last Modified : April 22, 2020
# BasicUDPServer.py


from socket import *
import datetime


# Class for translate App header & Data
class AppPacket :
    def __init__(self,data) :
        data = str(data)
        self.mode = int(data[0])
        self.data = data[1:] 



# Set UDP Server Port
serverPort = 30937

# Create UDP socket
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print("The server is ready to receive on port", serverPort)


# Record server start time
srv_start_time = datetime.datetime.now()


# try catch for handling Ctrl+C Situation
try :
    # While Loop for Waiting new client
    while (True) :
        raw, clientAddress = serverSocket.recvfrom(2048) 
        print('Connection requested from', clientAddress)
        
        # When clinet disconnected, it will get 0
        if len(raw) == 0 :
            break
        
        # mode 0~5
        # 0 : Select Menu
        # 1 ~ 5 : For Option 1~5
        
        # Data : String form 'Command number + data'
        # Ex) Command 1, text : Hello World!
        # It will send string : '1Hello World!'
        # Translate raw data
    
        in_data = AppPacket(raw.decode())
       
        # For each command, Different serve
        if in_data.mode == 1 :
            print("Command ",in_data.mode)
            mode = '1'
            
            # Get upper characters
            data = in_data.data.upper()
            raw = mode + data

            # Send to Client
            serverSocket.sendto(raw.encode(),clientAddress)
        
        elif in_data.mode == 2 :
            print("Command ",in_data.mode)
            mode = '2'
            # Get Client IP Address & Port
            data = 'Reply from server: IP = {}, port = {}'.format(clientAddress[0],clientAddress[1])
            raw = mode + data
            # Send to Client
            serverSocket.sendto(raw.encode(),clientAddress)
        elif in_data.mode == 3 :
            print("Command ",in_data.mode)
            mode = '3'
            # Get Local server time
            srv_time = datetime.datetime.now()
            data = "time = {:02d}:{:02d}:{:02d}".format(srv_time.hour,srv_time.minute,srv_time.second)
            raw = mode + data
            # Send to Client
            serverSocket.sendto(raw.encode(),clientAddress)
        elif in_data.mode == 4 :
            print("Command ",in_data.mode)
            mode = '4'
            # Get Running time
            run_time = datetime.datetime.now() - srv_start_time
            run_time = run_time.seconds
            hours, remainder = divmod(run_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            data = "run time = {:02d}:{:02d}:{:02d}".format(hours,minutes,seconds)
            raw = mode + data
            # Send to Client
            serverSocket.sendto(raw.encode(),clientAddress)

        elif in_data.mode == 5 :
            # Socket For client is closed
            print("Command ",in_data.mode)
            connectionSocket.close()
            print('Socket For Client is closed ')

            # Server is waiting new client Now.
            break


except (KeyboardInterrupt) :
    # For Ctrl + C on server
    None

# Close Server Socket
serverSocket.close()
print("\nBye bye~")
