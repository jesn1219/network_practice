import socket
import select
import os
import sys


C_HEADER_LENGTH = 2
HEADER_LENGTH = 10
F_HEADER_LENGTH = 20
SERVER_VERSION = "2.35"


IP = "nsl2.cau.ac.kr"
PORT = 20937

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


# dedicate server ip and port
server_socket.bind((IP, PORT))

# This makes server listen to new connections
server_socket.listen()

# List of sockets for select.select()
sockets_list = [server_socket]

# List of connected clients
# socket will be key, values has username info
clients = {}

print('Chat server start. Listening for connections on {}:{}...'.format(IP,PORT))




# Handles message that received from client 
# This function only used in new connection check. So, command 7-8 is not included
def receive_message(client_socket):

    try:
        command_header = client_socket.recv(C_HEADER_LENGTH)
        command = int(command_header.decode('utf-8').strip())
        print("receive_message : Received command : {}".format(command))
        # command 0 means, message to saying others
        if command == 0 :
            # message header notify message length to receiver (Server)
            message_header = client_socket.recv(HEADER_LENGTH)

            # if message header is None, that clients closed socket
            if not len(message_header):
                return False

            # Decode header to int value
            command = int(command_header.decode('utf-8').strip())
            message_length = int(message_header.decode('utf-8').strip())

            # Returns command, message header, message content
            return {'command': command, 'header': message_header, 'data': client_socket.recv(message_length)}

        # command 1 : \users
        # command 2 : \wh <nickname> <message>
        # command 3 : \exit
        # command 4 : \version
        # command 5 : \rename <nickname>
        # command 6 : \rtt
       
        elif command == 1 or command == 2 or command == 4 or command == 5 or command == 6  :
            print("command check#1, {}".format(command))
            message_header = client_socket.recv(HEADER_LENGTH)
            # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
            if not len(message_header):
                return False
            # Convert header to int value
            command = int(command_header.decode('utf-8').strip())
            message_length = int(message_header.decode('utf-8').strip())
            # Returns command, message header, message content
            return {'command': command, 'header':message_header, 'data':client_socket.recv(message_length)} 
         
        
        
        # command 9 : Signal that client want to close socket
        elif command == 9 :
            message_header = client_socket.recv(HEADER_LENGTH)
            if not len(message_header):
                return False

            command = int(command_header.decode('utf-8').strip())
            message_length = int(message_header.decode('utf-8').strip())
            # Returns command, message header, message content
            return {'command': command, 'header': message_header, 'data': client_socket.recv(message_length)}


    except :
        # Other cases. it is exceptional
        return False


try :
    while True:
        #listening from sockets 
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)


        # Iterate over notified sockets
        for notified_socket in read_sockets:

            # If notified socket is a server socket - There is new connection
            if notified_socket == server_socket:

                # Accepts new client 
                client_socket, client_address = server_socket.accept()

                # Server receives message that contains nickname info
                user = receive_message(client_socket)


                # Checking the name is valid
                user_name = user['data'].decode('utf-8')
                check_flag = True
                if len(user_name) > 32 :
                    message = "Nickname Length Must not over 32".encode('utf-8')
                    check_flag = False
                for c in user_name :
                    if ((not c.isalpha()) and c != '-') :
                        check_flag = False 
                        message = "Nickname Must Only Includes alphabet or '-'".encode('utf-8')
                for c in clients.keys()  :
                    if clients[c]['data'].decode('utf-8') == user_name :
                        message = "that nickname is used by another user. cannot connect".encode('utf-8')
                        check_flag = False

                # Checking that Users over 10?
                if len(clients.keys()) >= 10 :
                        message = "chat room is full. Cannot Connect".encode('utf-8')
                        check_flag = False
                
                # Decline connection 
                if check_flag == False :
                    command = -1 
                    command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                    username = "Server".encode('utf-8')
                    username_header = "{:<{}}".format(len(username),HEADER_LENGTH).encode('utf-8')
                    message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                    client_socket.send(command_header + username_header + username + message_header + message)
                else :
                    # Accept connection
                    # If False - client disconnected before he sent his name
                    if user is False:
                        continue

                    # Add accepted socket to socket list
                    sockets_list.append(client_socket)


                    # Save user ip, port, nickname, nicknameheader
                    user_ip = client_address[0]
                    user_port = client_address[1]
                    user["ip"] = user_ip
                    user["port"] = user_port
                    clients[client_socket] = user


                    # Notify to All users that new user joined
                    command = 0
                    command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                    sender_name = "Server".encode('utf-8')
                    sender_header = "{:<{}}".format(len(sender_name),HEADER_LENGTH).encode('utf-8')
                    message = "[{} is connected. There are {} users in this chat room.]".format(user['data'].decode('utf-8'),len(clients.keys())).encode('utf-8')
                    message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                    message_2 = "[Welcome {} to cau-cse chat room at {}. You are {}th user.]".format(user['data'].decode('utf-8'), user_ip+":"+str(user_port), len(clients))
                    message_2 = message_2.encode('utf-8')
                    message_2_header = "{:<{}}".format(len(message_2),HEADER_LENGTH).encode('utf-8')

                    # Send that notify new user message, or Welcome message
                    for c in clients:
                        # But don't sent it to sender
                        if c != client_socket:
                            # Notify new user
                            c.send(command_header + sender_header + sender_name + message_header + message)
                        else :
                            # Send Welcome message
                            client_socket.send(command_header + sender_header + sender_name + message_2_header + message_2)


                    print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))


            # Else existing socket is sending a message
            else:
                # Receive message
                message = {} 
        

                # command 1 : \users
                # command 2 : \wh <nickname> <message>
                # command 3 : \exit
                # command 4 : \version
                # command 5 : \rename <nickname>
                # command 6 : \rtt
                # command 7 : \fsend
                # command 8 : \wsend
                # command 9 : client will be closed

                command_header = notified_socket.recv(C_HEADER_LENGTH)
                if not command_header :
                    print("Client {} disconnected".format(clients[notified_socket]['data'].decode('utf-8')))

                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    continue
               
                command = int(command_header.decode('utf-8').strip())
                print("Received command : {} from {}".format(command, clients[notified_socket]['data'].decode('utf-8')))
                # command 0 means, message to saying others
                if command == 0 :
                    # message header notify message length to receiver (Server)
                    message_header = notified_socket.recv(HEADER_LENGTH)

                    # if message header is None, that clients closed socket
                    if not len(message_header):
                        message = {}

                    # Decode header to int value
                    command = int(command_header.decode('utf-8').strip())
                    message_length = int(message_header.decode('utf-8').strip())

                    # Returns command, message header, message content
                    message = {'command': command, 'header': message_header, 'data': notified_socket.recv(message_length)}

               
                elif command == 1 or command == 2 or command == 4 or command == 5 or command == 6  :
                    message_header = notified_socket.recv(HEADER_LENGTH)
                    # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
                    if not len(message_header):
                        message = {}
                    # Convert header to int value
                    command = int(command_header.decode('utf-8').strip())
                    message_length = int(message_header.decode('utf-8').strip())
                    # Returns command, message header, message content
                    message =  {'command': command, 'header':message_header, 'data':notified_socket.recv(message_length)} 

                elif command == 7 :
                    #fsend    
                    message_header = notified_socket.recv(HEADER_LENGTH)
                    # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
                    if not len(message_header):
                        message = {} 
                    # Convert header to int value
                    command = 7
                    message_length = int(message_header.decode('utf-8').strip())
                    file_name = notified_socket.recv(message_length)

                    
                    file_header = notified_socket.recv(F_HEADER_LENGTH)
                    file_length = int(file_header.decode('utf-8').strip())
                    file_data = b'' 
                    BUFF_SIZE = 4096

                    while (file_length > len(file_data)) :
                        part = notified_socket.recv(BUFF_SIZE)
                        file_data += part

                    #file_data = client_socket.recv(file_length)
                    #file_data = client_socket.recv(file_length)
                    # Returns command, message header, message content

                    message =  {'command': command, 'header':message_header, 'file_name': file_name, 'file_data' : file_data} 

                elif command == 8 :
                    
                    message_header = notified_socket.recv(HEADER_LENGTH)
                    # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
                    if not len(message_header):
                        message = {}
                    # Convert header to int value
                    command = command
                    
                    receiver_name_length = int(message_header.decode('utf-8').strip())
                    receiver_name = notified_socket.recv(receiver_name_length)

                    file_name_header = notified_socket.recv(HEADER_LENGTH)
                    file_name_length = int(file_name_header.decode('utf-8').strip())
                    file_name = notified_socket.recv(file_name_length)
                    file_header = notified_socket.recv(F_HEADER_LENGTH)
                    file_length = int(file_header.decode('utf-8').strip())
                    file_data = b'' 
                    BUFF_SIZE = 4096

                    while (file_length > len(file_data)) :
                        part = notified_socket.recv(BUFF_SIZE)
                        file_data += part


                    # Returns command, message header, message content
                    message =  {'command': command, 'header':message_header, 'file_name': file_name, 'file_data' : file_data, 'receiver_name' : receiver_name}

                 
                
                
                # command 9 : Signal that client want to close socket
                elif command == 9 :
                    message_header = notified_socket.recv(HEADER_LENGTH)
                    if not len(message_header):
                        message = {}

                    command = int(command_header.decode('utf-8').strip())
                    message_length = int(message_header.decode('utf-8').strip())
                    # Returns command, message header, message content
                    message = {'command': command, 'header': message_header, 'data': client_socket.recv(message_length)}





                # If False, client disconnected
                if message == {}:
                    # Remove from list for socket.socket()
                    sockets_list.remove(notified_socket)

                    # Remove from our list of users
                    del clients[notified_socket]
                    continue
                # command 9 means that client wnat to close socket 
                elif message["command"] == 9 :
                    command = 0
                    command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                    username = "Server".encode('utf-8')
                    username_header = "{:<{}}".format(len(username),HEADER_LENGTH).encode('utf-8')
                    message = "[ {} left. There are {} users now ]".format(clients[notified_socket]['data'].decode('utf-8'), -1+ len(clients))
                    message = message.encode('utf-8')
                    message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                    
                    for client_socket in clients:

                        # Send to other clients
                        if client_socket != notified_socket:

                            client_socket.send(command_header + username_header + username+ message_header + message)
                
                # command 0 almostly means that received  normal chat message
                elif message["command"] == 0 :
                    # Get user by notified socket, so we will know who sent the message
                    user = clients[notified_socket]

                    print('message content :{}'.format(message['data'].decode('utf-8')))
                    message_check = message['data'].decode('utf-8')

                    # Checking forbiddened phase
                    if 'i hate professor' in message_check.lower() :
                        message = "Forbidden phase is detected".encode('utf-8')
                        command = -1 
                        command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                        username = "Server".encode('utf-8')
                        username_header = "{:<{}}".format(len(username),HEADER_LENGTH).encode('utf-8')
                        message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                        notified_socket.send(command_header + username_header + username + message_header + message)
                    else :

                        # Iterate over connected clients and broadcast message
                        command = 0
                        command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')

                        for client_socket in clients:

                            # But don't sent it to sender
                            if client_socket != notified_socket:

                                # Send user and message (both with their headers)
                                # We are reusing here message header sent by sender, and saved username header send by user when he connected
                                client_socket.send(command_header + user['header'] + user['data'] + message['header'] + message['data'])


                elif message["command"] == 1 : 
                    print("Check Users list")
                    command = 1
                    command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                    message = "List of connected users\n"
                    
                    
                    for c in clients.keys() :
                        client = clients[c]
                        message += "nickname : {}, IP : {}, Port : {}\n".format(client['data'].decode('utf-8'),client["ip"],client["port"])
                    message = message.encode('utf-8')
                    
                    message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                    notified_socket.send(command_header + message_header + message) 



                # whisper functions
                elif message["command"] == 2 :
                    print('whisper to {}'.format(message["data"].decode('utf-8')))
                    command = 2
                    target_username = message["data"].decode('utf-8') 
                    message = receive_message(notified_socket)
                    message = message['data']
                    message = message.decode('utf-8')
                    print('message : {}'.format(message))
                    message_check = message


                    # Check forbidden phase 
                    if 'i hate professor' in message_check.lower() :
                        message = "Forbidden phase is detected".encode('utf-8')
                        command = -1 
                        command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                        username = "Server".encode('utf-8')
                        username_header = "{:<{}}".format(len(username),HEADER_LENGTH).encode('utf-8')
                        message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                        notified_socket.send(command_header + username_header + username + message_header + message)
                    else : 

                        # Check target nickname is valid
                        flag = 0
                        for target_socket in clients.keys() :
                            if clients[target_socket]["data"].decode('utf-8') == target_username :
                                command = 0
                                command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                                message = "(whisper) {}".format(message)
                                message = message.encode('utf-8')
                                message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                                target_socket.send(command_header + user['header'] + user['data'] +  message_header + message)
                                flag = 1
                        # if target name is not exist
                        if flag == 0 :
                            command = 0
                            command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                            username = "System"
                            username_header = "{:<{}}".format(len(username),HEADER_LENGTH).encode('utf-8')
                            message = "'{}' is not in this chat room".format(target_username)
                            message = message.encode('utf-8')
                            message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                            notified_socket.send( command_header + username_header + username.encode('utf-8') + message_header + message)

                # Check the server and client version
                elif message['command'] == 4 :
                    print("Check version of server, client")
                    client_version = message['data'].decode('utf-8')
                    command = 0
                    command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                    username = "System"
                    username_header = "{:<{}}".format(len(username),HEADER_LENGTH).encode('utf-8')
                    message = "Server version : {}, Client version : {}".format(SERVER_VERSION,client_version)
                    message = message.encode('utf-8')
                    message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                    notified_socket.send( command_header + username_header + username.encode('utf-8') + message_header + message)

                # rename the nickname
                elif message['command'] == 5 :
                    new_name = message['data'].decode('utf-8')
                    print("Rename {} to {}".format(clients[notified_socket]['data'].decode('utf-8'),new_name))
                    new_name_header = message['header'].decode('utf-8')
                    name_check_flag = True

                    # Check that nickname is valid
                    if len(new_name) > 32 :
                        message = "Nickname Length Must not over 32".encode('utf-8')
                        name_check_flag = False
                    for c in new_name :
                        if ((not c.isalpha()) and c != '-') :
                            name_check_flag = False 
                            message = "Nickname Must Only Includes alphabet or '-'".encode('utf-8')
                    for c in clients.keys()  :
                        if clients[c]['data'].decode('utf-8') == new_name :
                            message = "Nickname is already exist in the chat room".encode('utf-8')
                            name_check_flag = False
                   
                    # if new nickname is not valid
                    if name_check_flag == False :
                        command = 0
                        command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                        username = "Server".encode('utf-8')
                        username_header = "{:<{}}".format(len(username),HEADER_LENGTH).encode('utf-8')
                        message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                        notified_socket.send(command_header + username_header + username + message_header + message)
                        print("Rename Failed")
                    # if new nickname is valied
                    else : 
                        command = 0
                        message = "Nickname is Successfully changed to {}".format(new_name).encode('utf-8')
                        command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                        username = "Server".encode('utf-8')
                        username_header = "{:<{}}".format(len(username),HEADER_LENGTH).encode('utf-8')
                        message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                        notified_socket.send(command_header + username_header + username + message_header + message)

                        message = "[ {} changed nickname to {} ]".format(clients[notified_socket]['data'].decode('utf-8'),new_name).encode('utf-8')
                        message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                        # Notify to other users
                        for client_socket in clients:

                            # But don't sent it to sender
                            if client_socket != notified_socket:
                                
                                client_socket.send(command_header + user['header'] + user['data'] + message_header + message)

                        # Update the user info
                        clients[notified_socket]['data'] = new_name.encode('utf-8')
                        clients[notified_socket]['header'] = new_name_header.encode('utf-8')
                        print("Rename Success")
                # Command for rtt check
                elif message['command'] == 6 :
                        command = 6
                        command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                        notified_socket.send(command_header)
                
                # fsend 
                elif message['command'] == 7 :
                    # Send notify to all
                    command = 7
                    command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                    username = clients[notified_socket]['data']
                    username_header = "{:<{}}".format(len(username),HEADER_LENGTH).encode('utf-8')
                    
                    file_name = message['file_name']
                    file_name_header = "{:<{}}".format(len(file_name),HEADER_LENGTH).encode('utf-8')
                    file_data = message['file_data']
                    file_header = "{:<{}}".format(len(file_data),F_HEADER_LENGTH).encode('utf-8')
                    
                    print("fsend. file name : {}, file size : {} bytes".format(file_name.decode('utf-8'),file_header.decode('utf-8')))
                    

                    for client_socket in clients :
                        # But don't sent it to sender
                        if client_socket != notified_socket:
                            #print("target name : ",clients[client_socket]['data'].decode('utf-8'))
                            receiver_name = clients[client_socket]['data']
                            print("fsend to {}.".format(receiver_name.decode('utf-8')))
                            receiver_name_header = "{:<{}}".format(len(receiver_name),HEADER_LENGTH).encode('utf-8')
                            client_socket.send(command_header + username_header + username+ file_name_header+file_name+file_header+receiver_name_header + receiver_name) 
                            file_data_buf = file_data
                            BUFF_SIZE = 4096
                            while(len(file_data_buf) > BUFF_SIZE) :
                                part = file_data_buf[:BUFF_SIZE]
                                client_socket.send(part)
                                file_data_buf = file_data_buf[BUFF_SIZE:]
                            client_socket.send(file_data_buf)
                            print("fsend to {} is complete.".format(receiver_name.decode('utf-8')))

                elif message['command'] == 8 :
                    # Send notify to all
                    command = 8
                    command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                    username = clients[notified_socket]['data']
                    username_header = "{:<{}}".format(len(username),HEADER_LENGTH).encode('utf-8')
                    receiver_name = message['receiver_name']
                    receiver_name_header = "{:<{}}".format(len(receiver_name),HEADER_LENGTH).encode('utf-8')
                  

                    file_name = message['file_name']
                    file_name_header = "{:<{}}".format(len(file_name),HEADER_LENGTH).encode('utf-8')
                    file_data = message['file_data']
                    file_header = "{:<{}}".format(len(file_data),F_HEADER_LENGTH).encode('utf-8')
                    
                    print("wsend. file name : {}, file size : {} bytes".format(file_name.decode('utf-8'),file_header.decode('utf-8')))

                    # Check target nickname is valid
                    flag = 0
                    for target_socket in clients.keys() :
                        if clients[target_socket]["data"] == receiver_name :
                            flag = 1
                    # if target name is not exist
                    if flag == 0 :
                        command = 0
                        command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                        username = "System"
                        username_header = "{:<{}}".format(len(username),HEADER_LENGTH).encode('utf-8')
                        message = "'{}' is not in this chat room".format(receiver_name.decode('utf-8'))
                        message = message.encode('utf-8')
                        message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                        notified_socket.send( command_header + username_header + username.encode('utf-8') + message_header + message)
                    else :
                        for client_socket in clients :
                            # But don't sent it to sender
                            if clients[client_socket]['data'] == receiver_name:
                                client_socket.send(command_header + username_header + username+ file_name_header+file_name+file_header + receiver_name_header +receiver_name)
                                BUFF_SIZE = 4096
                                while(len(file_data) > BUFF_SIZE) :
                                    part = file_data[:BUFF_SIZE]
                                    client_socket.send(part)
                                    file_data = file_data[BUFF_SIZE:]
                                client_socket.send(file_data)
                                break

        for notified_socket in exception_sockets:

            # Remove from list for socket.socket()
            sockets_list.remove(notified_socket)

            # Remove from our list of users
            del clients[notified_socket]
except Exception as e :
        # Server close
        _, _ , tb = sys.exc_info() # tb -> traceback object print 'file name = ', __file__ print 'error line No = {}'.format(tb.tb_lineno) print e
        print('file name = ', __file__)
        print('error line No = {}'.format(tb.tb_lineno))
        print(e)
        server_socket.close()
        print("Server closed")
        os._exit(0)
