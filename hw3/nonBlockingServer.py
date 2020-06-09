# Submitter :
# Jesoon Kang, 20170937
# Last Modified : April 22, 2020
# MultiThreadTCPServer.py


from socket import *
from _thread import *
import threading
import time
import datetime
import select



# Class for translate App header & Data
class AppPacket :
    def __init__(self,data) :
        data = str(data)
        self.mode = int(data[0])
        self.data = data[1:] 



# Set TCP Server Port
serverPort = 20937




def check_status(sec) :
    run_time = datetime.datetime.now() - server_start_time
    run_time = run_time.seconds
    hours, remainder = divmod(run_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    if (seconds%sec) == 0 :
        print("Number of clients : {:d}  Server running time : {:02d}:{:02d}:{:02d}".format(len(connected_clients),hours,minutes,seconds))
        time.sleep(1)

def get_client_id(socket) :
    for key, value in connected_clients.items() :
        if value == socket :
            return key
    return -1 


# try catch for handling Ctrl+C Situation
client_id = 0
connected_clients = {}



try :
    # Create TCP socket
    # Set server start time 
    server_start_time = datetime.datetime.now()
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', serverPort))
    serverSocket.listen(0)
    print("The server is ready to receive on port", serverPort)

    connection_list = [serverSocket]
    # While Loop for Waiting new client
    while (connection_list) :
        check_status(60)
        read_socket, write_socket, error_socket = select.select(connection_list, [], [], 1)
        for socket in read_socket :
            if socket == serverSocket :
                (connectionSocket, clientAddress) = socket.accept()
                client_id += 1
                print('Connection requested from', clientAddress)
                connected_clients[client_id] = connectionSocket
                connection_list.append(connectionSocket)
                print("Client {:d} connected. Number of connected clients = {:d}".format(client_id,len(connected_clients)))
            else :
                # connected_clients
                #Socket
                try :
                    raw = socket.recv(2048)
                    if raw : 
                        # When client disconnected, it will get 0
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
                            socket.send(raw.encode())
                        
                        elif in_data.mode == 2 :
                            print("Command ",in_data.mode)
                            mode = '2'
                            # Get Client IP Address & Port
                            data = 'Reply from server: IP = {}, port = {}'.format(clientAddress[0],clientAddress[1])
                            raw = mode + data
                            socket.send(raw.encode())
                        elif in_data.mode == 3 :
                            print("Command ",in_data.mode)
                            mode = '3'
                            # Get Local server time
                            srv_time = datetime.datetime.now()
                            data = "time = {:02d}:{:02d}:{:02d}".format(srv_time.hour,srv_time.minute,srv_time.second)
                            raw = mode + data
                            socket.send(raw.encode())
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
                            socket.send(raw.encode())

                        elif in_data.mode == 5 :
                            # Socket For client is closed
                            print("Command ",in_data.mode)
                            client_id = get_client_id(socket) 
                            connected_clients.pop(client_id,None)
                            connection_list.remove(socket)
                            socket.close()
                            print("Client {:d} disconnected. Number of connected clients = {:d}".format(client_id,len(connected_clients)))
                            break
                    else : 
                        client_id = get_client_id(socket) 
                        connected_clients.pop(client_id,None)
                        connection_list.remove(socket)
                        socket.close()
                        print("Client {:d} disconnected. Number of connected clients = {:d}".format(client_id,len(connected_clients)))
                except (KeyboardInterrupt, NameError) :
                    # For Ctrl + C on server
                    # Close Connection Socket
                    try :
                        client_id = get_client_id(socket) 
                        connected_clients.pop(client_id,None)
                        connection_list.remove(socket)
                        socket.close()
                        print("Client {:d} disconnected. Number of connected clients = {:d}".format(client_id,len(connected_clients)))
                    except (NameError):
                        None



except (KeyboardInterrupt, NameError) as e:
    print("Server is shutting down")
    for socket in connection_list :
        if not socket == serverSocket :
            socket.close()
            client_id = get_client_id(socket) 
            connected_clients.pop(client_id,None)
            connection_list.remove(socket)
            print("Client {:d} disconnected. Number of connected clients = {:d}".format(client_id,len(connected_clients)))
    serverSocket.close()


# Close Server Socket
serverSocket.close()
print("\nBye bye~")
