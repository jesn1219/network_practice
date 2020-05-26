import socket
import select

C_HEADER_LENGTH = 2
HEADER_LENGTH = 10
SERVER_VERSION = "1.1"


IP = "127.0.0.1"
PORT = 1234

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SO_ - socket option
# SOL_ - socket option level
# Sets REUSEADDR (as a socket option) to 1 on socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind, so server informs operating system that it's going to use given IP and port
# For a server using 0.0.0.0 means to listen on all available interfaces, useful to connect locally to 127.0.0.1 and remotely to LAN interface IP
server_socket.bind((IP, PORT))

# This makes server listen to new connections
server_socket.listen()

# List of sockets for select.select()
sockets_list = [server_socket]

# List of connected clients - socket as a key, user header and name as data
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')


def name_check(name) :
    if len(name) > 32 :
        return False
    for char in name :
        if not (c.isalpha() or '-') :
            return False
    return True

def name_exist_check(name) :
    for target_socket in clients.keys() :
        if clients[target_socket]["data"].decode('utf-8') == name :
            return False
    return True



# Handles message receiving
def receive_message(client_socket):

    try:
        command_header = client_socket.recv(C_HEADER_LENGTH)
        command = int(command_header.decode('utf-8').strip())


        if command == 0 :
            # Receive our "header" containing message length, it's size is defined and constant
            message_header = client_socket.recv(HEADER_LENGTH)

            # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
            if not len(message_header):
                return False

            # Convert header to int value
            command = int(command_header.decode('utf-8').strip())
            message_length = int(message_header.decode('utf-8').strip())

            # Return an object of message header and message data
            return {'command': command, 'header': message_header, 'data': client_socket.recv(message_length)}
        elif command == 1 or command == 2 or command == 4 or command == 5 or command == 6 or command ==7 :
            message_header = client_socket.recv(HEADER_LENGTH)
            # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
            if not len(message_header):
                return False
            # Convert header to int value
            command = int(command_header.decode('utf-8').strip())
            message_length = int(message_header.decode('utf-8').strip())

            return {'command': command, 'header':message_header, 'data':client_socket.recv(message_length)} 


    except :
        # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
        # or just lost his connection
        # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
        # and that's also a cause when we receive an empty message
        return False

while True:

    # Calls Unix select() system call or Windows select() WinSock call with three parameters:
    #   - rlist - sockets to be monitored for incoming data
    #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
    #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
    # Returns lists:
    #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
    #   - writing - sockets ready for data to be send thru them
    #   - errors  - sockets with some exceptions
    # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)


    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:

            # Accept new connection
            # That gives us new socket - client socket, connected to this given client only, it's unique for that client
            # The other returned object is ip/port set
            client_socket, client_address = server_socket.accept()

            # Client should send his name right away, receive it
            user = receive_message(client_socket)


            user_name = user['data'].decode('utf-8')
            check_flag = True
            if len(user_name) > 32 :
                print("length")
                message = "Nickname Length Must not over 32".encode('utf-8')
                check_flag = False
            for c in user_name :
                if (not c.isalpha() or c == '-') :
                    check_flag = False 
                    message = "Nickname Must Only Includes alphabet or '-'".encode('utf-8')
            for c in clients.keys()  :
                print(clients[c]['data'])
                if clients[c]['data'].decode('utf-8') == user_name :
                    message = "Nickname is already exist in the chatting room".encode('utf-8')
                    check_flag = False
            if len(clients.keys()) >= 10 :
                    message = "Chatting room is full. Cannot Connect".encode('utf-8')
                    check_flag = False
                
           
            if check_flag == False :
                command = -1 
                command_header = f"{command:<{C_HEADER_LENGTH}}".encode('utf-8')
                username = "Server".encode('utf-8')
                username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                client_socket.send(command_header + username_header + username + message_header + message)
            else :
                # If False - client disconnected before he sent his name
                if user is False:
                    continue

                # Add accepted socket to select.select() list
                sockets_list.append(client_socket)

                # Also save username and username header
                user_ip = client_address[0]
                user_port = client_address[1]
                user["ip"] = user_ip
                user["port"] = user_port
                clients[client_socket] = user

                print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

        # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)

            print(message)
            # If False, client disconnected, cleanup
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del clients[notified_socket]

                continue
            elif message["command"] == 0 :
                # Get user by notified socket, so we will know who sent the message
                user = clients[notified_socket]

                print(f'Received message from {user["data"].decode("utf-8")}: Command : {message["command"]} {message["data"].decode("utf-8")}')
                message_check = message['data'].decode('utf-8')
                if 'i hate professor' in message_check.lower() :
                    message = "Forbidden phase is detected".encode('utf-8')
                    command = -1 
                    command_header = f"{command:<{C_HEADER_LENGTH}}".encode('utf-8')
                    username = "Server".encode('utf-8')
                    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
                    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                    client_socket.send(command_header + username_header + username + message_header + message)


                # Iterate over connected clients and broadcast message
                command = 0
                command_header = f"{command:<{C_HEADER_LENGTH}}".encode('utf-8')

                for client_socket in clients:

                    # But don't sent it to sender
                    if client_socket != notified_socket:

                        # Send user and message (both with their headers)
                        # We are reusing here message header sent by sender, and saved username header send by user when he connected
                        client_socket.send(command_header + user['header'] + user['data'] + message['header'] + message['data'])


            elif message["command"] == 1 : 
                command = 1
                command_header = f"{command:<{C_HEADER_LENGTH}}".encode('utf-8')
                message = "List of connected users\n"
                
                
                for c in clients.keys() :
                    client = clients[c]
                    message += "nickname : {}, IP : {}, Port : {}\n".format(client['data'].decode('utf-8'),client["ip"],client["port"])
                print(message)
                message = message.encode('utf-8')
                
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                notified_socket.send(command_header + message_header + message) 
                print("command 1 sended")




            elif message["command"] == 2 :
                print(f'Received message from {user["data"].decode("utf-8")}: Command : {message["command"]} {message["data"].decode("utf-8")}')
                command = 2
                target_username = message["data"].decode('utf-8') 
                message = receive_message(notified_socket)
                print(f'whisper message from {user["data"].decode("utf-8")}: Command : {message["command"]} {message["data"].decode("utf-8")}')
                message = message['data']
                message = message.decode('utf-8')
                
                flag = 0
                for target_socket in clients.keys() :
                    if clients[target_socket]["data"].decode('utf-8') == target_username :
                        command = 0
                        command_header = f"{command:<{C_HEADER_LENGTH}}".encode('utf-8')
                        message = "(whisper) {}".format(message)
                        message = message.encode('utf-8')
                        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                        print(command_header, message_header,message) 
                        print(target_socket)
                        target_socket.send(command_header + user['header'] + user['data'] +  message_header + message)
                        flag = 1
                if flag == 0 :
                    command = 0
                    command_header = f"{command:<{C_HEADER_LENGTH}}".encode('utf-8')
                    username = "System"
                    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
                    message = "'{}' is not in this chatting room".format(target_username)
                    message = message.encode('utf-8')
                    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                    notified_socket.send( command_header + username_header + username.encode('utf-8') + message_header + message)


            elif message['command'] == 4 :
                client_version = message['data'].decode('utf-8')
                
                command = 0
                command_header = f"{command:<{C_HEADER_LENGTH}}".encode('utf-8')
                username = "System"
                username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
                message = "Server version : {}, Client version : {}".format(SERVER_VERSION,client_version)
                message = message.encode('utf-8')
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                notified_socket.send( command_header + username_header + username.encode('utf-8') + message_header + message)

            elif message['command'] == 5 :
                new_name = message['data'].decode('utf-8')
                name_check_flag = True
                if len(new_name) > 32 :
                    print("length")
                    message = "Nickname Length Must not over 32".encode('utf-8')
                    name_check_flag = False
                for c in new_name :
                    if (not c.isalpha() or c == '-') :
                        name_check_flag = False 
                        message = "Nickname Must Only Includes alphabet or '-'".encode('utf-8')
                for c in clients.keys()  :
                    print(clients[c]['data'])
                    if clients[c]['data'].decode('utf-8') == new_name :
                        message = "Nickname is already exist in the chatting room".encode('utf-8')
                        name_check_flag = False
                print("name check : ", name_check_flag)
                if name_check_flag == False :
                    command = 0
                    command_header = f"{command:<{C_HEADER_LENGTH}}".encode('utf-8')
                    username = "Server".encode('utf-8')
                    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
                    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                    notified_socket.send(command_header + username_header + username + message_header + message)
                else : 
                    command = 0
                    message = "Nickname is Successfully changed to {}".format(new_name).encode('utf-8')
                    command_header = f"{command:<{C_HEADER_LENGTH}}".encode('utf-8')
                    username = "Server".encode('utf-8')
                    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
                    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                    notified_socket.send(command_header + username_header + username + message_header + message)
                    clients[notified_socket]['data'] = new_name.encode('utf-8')
            elif message['command'] == 6 :
                    command = 6
                    command_header = f"{command:<{C_HEADER_LENGTH}}".encode('utf-8')
                    notified_socket.send(command_header)

            ''' Delete 
            elif message['command'] == 7 :
                # name check
                #
                username = message['data'].decode('utf-8')
                message = ""
                if name_check(username) :
                    if name_exist_check(username) :
                        message = "Username is valid"
                        command = 7
                    else :
                        message = "that nickname is used by another user. cannot connect"
                        command = 0
                else : 
                    message = "invalid nickname. nickname length must <=32, Only alphabet and '-'"
                    command = 0 
                command_header = f"{command:<{C_HEADER_LENGTH}}".encode('utf-8')
                print(message,command)
                message = message.encode('utf-8')
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                notified_socket.send( command_header + message_header + message)

            '''
    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]

