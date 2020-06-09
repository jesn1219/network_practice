# Submitter :
# Jesoon Kang, 20170937
# Last Modified : April 20, 2020
# BasicUDPClient.py

from socket import *
import datetime


# Class for translate App header & Data
class AppPacket :
    def __init__(self,data) :
        data = str(data)
        self.mode = int(data[0])
        self.data = data[1:] 


# Set TCP Server Address & Port
serverName = '192.168.0.10'
serverPort = 20002

# List for Menu Options 
menu_options = \
    ['convert text to UPPER-case',\
     'get my IP address and port number',\
     'get server time',\
     'get server running time',\
     'exit'\
     ]

# Function for display menu options
def menu_present() :
    print("\n<Menu>")
    for i,opt in enumerate(menu_options) :
        print(i+1,") ",opt)
    print("")


# Create Client UDP Socket 
clientSocket = socket(AF_INET, SOCK_DGRAM)
# Set timeout
clientSocket.settimeout(.02)
print("The client is running on port", clientSocket.getsockname()[1])



# try catch for handling Ctrl+C Situation
try :
    # mode 0~5
    # 0 : Select Menu
    # 1 ~ 5 : For Option 1~5
  
    # Data : String form 'Command number + data'
    # Ex) Command 1, text : Hello World!
    # It will send string : '1Hello World!'
    mode = 0
    while (True) :
        if mode == 0 : 
            # Present Menu Options
            menu_present()

            # Input Command
            mode = input("Input option: ")
           
            # Check input option
            try :
                mode = int(mode) 
            except (ValueError) :
                None
            if mode in range(1,len(menu_options)+1):
                None
            else :
                print("Not available option")
                mode = 0

        elif mode == 1 :
            # input text
            data = input('Input lowercase sentence: ')
            # Attach header
            raw = str(mode) + data
            
            # Send to Server and Record Send time 
            sent_time = datetime.datetime.now()
            clientSocket.sendto(raw.encode(), (serverName, serverPort))
            
            # Receive data from Server
            try : 
                ret_raw = clientSocket.recv(2048)
                received_time = datetime.datetime.now() 
            except timeout :
                print("Timed out : Connection Failed")
                break
            
            # Unpack return data
            ret_data = AppPacket(ret_raw.decode())
            print("Reply from server : ",ret_data.data)
            # Get RTT 
            response_time = (received_time - sent_time).microseconds * 0.001
            print("Response time : {:.2f} ms".format(response_time))
            mode = 0
        
        elif mode == 2 :
            raw = str(mode)
            # Send to Server and Record Send time 
            sent_time = datetime.datetime.now()
            clientSocket.sendto(raw.encode(), (serverName, serverPort))
            
            # Receive data from Server
            try : 
                ret_raw = clientSocket.recv(2048)
                received_time = datetime.datetime.now() 
            except timeout :
                print("Timed out : Connection Failed")
                break
            # Unpack return data
            ret_data = AppPacket(ret_raw.decode())
            print("Reply from server : ",ret_data.data)
            # Get RTT 
            response_time = (received_time - sent_time).microseconds * 0.001
            print("Response time : {:.2f} ms".format(response_time))
            mode = 0
        elif mode == 3 :
            raw = str(mode)
            # Send to Server and Record Send time 
            sent_time = datetime.datetime.now()
            clientSocket.sendto(raw.encode(), (serverName, serverPort))
            
            # Receive data from Server
            try : 
                ret_raw = clientSocket.recv(2048)
                received_time = datetime.datetime.now() 
            except timeout :
                print("Timed out : Connection Failed")
                break
            # Unpack return data
            ret_data = AppPacket(ret_raw.decode())
            print("Reply from server : ",ret_data.data)
            # Get RTT 
            response_time = (received_time - sent_time).microseconds * 0.001
            print("Response time : {:.2f} ms".format(response_time))
            mode = 0
        elif mode == 4 :
            raw = str(mode)
            # Send to Server and Record Send time 
            sent_time = datetime.datetime.now()
            clientSocket.sendto(raw.encode(), (serverName, serverPort))
            
            # Receive data from Server
            try : 
                ret_raw = clientSocket.recv(2048)
                received_time = datetime.datetime.now() 
            except timeout :
                print("Timed out : Connection Failed")
                break
            
            # Unpack return data
            ret_data = AppPacket(ret_raw.decode())
            print("Reply from server : ",ret_data.data)
            # Get RTT 
            response_time = (received_time - sent_time).microseconds * 0.001
            print("Response time : {:.2f} ms".format(response_time))
            mode = 0

        elif mode == 5 :
            ret_raw = '5'
            clientSocket.sendto(raw.encode(), (serverName, serverPort))
            print("Terminate Connection")
            break

except (KeyboardInterrupt) :
    None

# Close Client Socket
clientSocket.close()
print('\nBye bye~')
