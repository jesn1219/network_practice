# Submitter :
# Jesoon Kang, 20170937
# Last Modified : April 22, 2020
# MultiThreadTCPServer.py


from socket import *
from _thread import *
import threading
import time
import datetime




# Class for translate App header & Data
class AppPacket :
    def __init__(self,data) :
        data = str(data)
        self.mode = int(data[0])
        self.data = data[1:] 



# Set TCP Server Port
serverPort = 20937

class Thread_param :
    def __init__(self,c,client_id) :
        self.connectionSocket = c
        self.client_id = client_id




def status_thread() :
    while(True) :
        run_time = datetime.datetime.now() - server_start_time
        run_time = run_time.seconds
        hours, remainder = divmod(run_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        if (seconds == 0) :
            data = "run time = {:02d}:{:02d}:{:02d}".format(hours,minutes,seconds)
            print(data)
            print("Number of clients : {:d}".format(len(connected_clients)))
            time.sleep(1)

def threaded(param) :
    connectionSocket = param.connectionSocket
    client_id = param.client_id

    try :
        while(True) :
            raw = connectionSocket.recv(2048)
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
                connectionSocket.send(raw.encode())
            
            elif in_data.mode == 2 :
                print("Command ",in_data.mode)
                mode = '2'
                # Get Client IP Address & Port
                data = 'Reply from server: IP = {}, port = {}'.format(clientAddress[0],clientAddress[1])
                raw = mode + data
                connectionSocket.send(raw.encode())
            elif in_data.mode == 3 :
                print("Command ",in_data.mode)
                mode = '3'
                # Get Local server time
                srv_time = datetime.datetime.now()
                data = "time = {:02d}:{:02d}:{:02d}".format(srv_time.hour,srv_time.minute,srv_time.second)
                raw = mode + data
                connectionSocket.send(raw.encode())
            elif in_data.mode == 4 :
                print("Command ",in_data.mode)
                mode = '4'
                # Get Running time
                run_time = datetime.datetime.now() - server_start_time
                run_time = run_time.seconds
                hours, remainder = divmod(run_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                data = "run time = {:02d}:{:02d}:{:02d}".format(hours,minutes,seconds)
                raw = mode + data
                connectionSocket.send(raw.encode())

            elif in_data.mode == 5 :
                # Socket For client is closed
                print("Command ",in_data.mode)
                connectionSocket.close()

                # Server is waiting new client Now.
                break
    except (KeyboardInterrupt) :
        print("keyboardinterrupt is detected in thread")
        connectionSocket.close()

    # Remove client on dictionary
    connectionSocket.close()
    connected_clients.pop(client_id,None)
    print("Client {:d} disconnected. Number of connected clients = {:d}".format(client_id,len(connected_clients)))





# try catch for handling Ctrl+C Situation
#
id_client = 0
connected_clients = {}
try :
    # Create TCP socket
    # Set server start time 
    server_start_time = datetime.datetime.now()
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', serverPort))
    serverSocket.listen(0)
    print("The server is ready to receive on port", serverPort)
    start_new_thread(status_thread,())

    # While Loop for Waiting new client
    while (True) :
        (connectionSocket, clientAddress) = serverSocket.accept()
        id_client += 1
        thread_param = Thread_param(connectionSocket,id_client)
        print('Connection requested from', clientAddress)
        start_new_thread(threaded,(thread_param,))
        
        connected_clients[thread_param.client_id] = thread_param
        print("Client {:d} connected. Number of connected clients = {:d}".format(thread_param.client_id,len(connected_clients)))
    serverSocket.close()

except (KeyboardInterrupt, NameError) :
    # For Ctrl + C on server
    # Close Connection Socket
    try :
        serverSocket.close()
        connectionSocket.close()
    except (NameError):
        None


# Close Server Socket
serverSocket.close()
print("\nBye bye~")
