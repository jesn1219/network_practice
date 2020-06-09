import socket
import select
import errno
import threading
from _thread import *
import sys, getopt
import os
import datetime


C_HEADER_LENGTH = 2
HEADER_LENGTH = 10
F_HEADER_LENGTH = 20
CLIENT_VERSION = "2.23"

SERVER_IP = "nsl2.cau.ac.kr"
SERVER_PORT = 20937 
sent_time = datetime.datetime.now()
received_time = datetime.datetime.now()



# get user nickname
try :
    username = sys.argv[1].encode('utf-8')
except IndexError :
    print("Input Nickname arguement")
    os._exit(0)

# Create client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server
try :
    client_socket.connect((SERVER_IP, SERVER_PORT))
except :
    print("Server is closed")
    os._exit(0)

client_socket.setblocking(True)

# Check nickname. through sending nickname check message to seaver
command = 0
command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
username_header = "{:<{}}".format(len(username),HEADER_LENGTH).encode('utf-8')
client_socket.send(command_header+ username_header + username)

# when client dead, sending server last message
send_last_msg = False


# thread that print out message
def threaded() :
    while (True) :
        try:
            while True:
                command_header = client_socket.recv(C_HEADER_LENGTH)
                command = int(command_header.decode('utf-8').strip())

                # Print out normal message
                if command == 0 :

                    # user header contains client user name length
                    username_header = client_socket.recv(HEADER_LENGTH)

                    if not len(username_header):
                        print('Connection closed by the server')
                        sys.exit()

                    # Convert header to int value
                    username_length = int(username_header.decode('utf-8').strip())

                    # Receive and decode username
                    username = client_socket.recv(username_length).decode('utf-8')


                    # message header contains message length info
                    message_header = client_socket.recv(HEADER_LENGTH)
                    message_length = int(message_header.decode('utf-8').strip())
                    message = client_socket.recv(message_length).decode('utf-8')

                    print('{} > {}'.format(username,message))
                elif command == 7 :
                    # user header contains client user name length
                    username_header = client_socket.recv(HEADER_LENGTH)

                    if not len(username_header):
                        print('Connection closed by the server')
                        sys.exit()

                    # Convert header to int value
                    username_length = int(username_header.decode('utf-8').strip())

                    # Receive and decode username
                    username = client_socket.recv(username_length).decode('utf-8')
                    
                    # message header contains message length info
                    file_name_header = client_socket.recv(HEADER_LENGTH)
                    file_name_length = int(file_name_header.decode('utf-8').strip())
                    file_name = client_socket.recv(file_name_length).decode('utf-8')
                    file_header = client_socket.recv(F_HEADER_LENGTH)
                    file_length = int(file_header.decode('utf-8').strip())
                    receiver_name_header = client_socket.recv(HEADER_LENGTH)
                    receiver_name_length = int(receiver_name_header.decode('utf-8').strip())
                    receiver_name = client_socket.recv(receiver_name_length).decode('utf-8')
                    BUFF_SIZE = 1024 
                    file_data = b''
                    while (True) :
                        part = client_socket.recv(BUFF_SIZE)
                        file_data += part
                        if (len(part)<BUFF_SIZE) :
                            break


                    file_name = "fsend_"+username+"_"+receiver_name+"_"+file_name
                    print("fsend from {}. file name : {}, file size : {}".format(username,file_name,file_length))
                    print("Writing file '{}'...".format(file_name))
                    with open(file_name,'wb') as file :
                        file.write(file_data)
                        print("File downloaded successfully!".format(username))
                
                
                elif command == 8 :
                    # user header that contains sender's username length
                    username_header = client_socket.recv(HEADER_LENGTH)

                    if not len(username_header):
                        print('Connection closed by the server')
                        sys.exit()

                    # Convert header to int value
                    username_length = int(username_header.decode('utf-8').strip())

                    # Receive and decode username
                    username = client_socket.recv(username_length).decode('utf-8')
                    
                    # message header contains message length info
                    file_name_header = client_socket.recv(HEADER_LENGTH)
                    file_name_length = int(file_name_header.decode('utf-8').strip())
                    file_name = client_socket.recv(file_name_length).decode('utf-8')
                    file_header = client_socket.recv(F_HEADER_LENGTH)
                    file_length = int(file_header.decode('utf-8').strip())
                    receiver_name_header = client_socket.recv(HEADER_LENGTH)
                    receiver_name_length = int(receiver_name_header.decode('utf-8').strip())
                    receiver_name = client_socket.recv(receiver_name_length).decode('utf-8')
                    BUFF_SIZE = 1024 
                    file_data = b''
                    while (file_length > len(file_data)) :
                        part = client_socket.recv(BUFF_SIZE)
                        file_data += part

                    file_name = "wsend_"+username+"_"+receiver_name+"_"+file_name
                    print("wsend from {}. file name : {}, file size : {}".format(username,file_name,file_length))
                    print("Writing file '{}'...".format(file_name))
                    with open(file_name,'wb') as file :
                        file.write(file_data)
                        print("wsend from {}. File received successfully!".format(username))



                elif command == 1 :
                    # command 1 is print out user list
                    message_header = client_socket.recv(HEADER_LENGTH)
                    if not len(message_header):
                        print('Connection closed by the server')
                        break
                    message_length = int(message_header.decode('utf-8').strip())
                    message = client_socket.recv(message_length).decode('utf-8')
                    print(message)
               
                # command 6 is rtt check command
                elif command == 6 :
                    received_time = datetime.datetime.now()
                    response_time = (received_time - sent_time).microseconds * 0.001
                    print("Round-Trip-Time : {} ms".format(response_time))
                
                # command -1 means force closed
                elif command == -1 :
                    username_header = client_socket.recv(HEADER_LENGTH)

                    if not len(username_header):
                        print('Connection closed by the server')
                        sys.exit()

                    username_length = int(username_header.decode('utf-8').strip())
                    username = client_socket.recv(username_length).decode('utf-8')
                    message_header = client_socket.recv(HEADER_LENGTH)
                    message_length = int(message_header.decode('utf-8').strip())
                    message = client_socket.recv(message_length).decode('utf-8')
                    
                    
                    print('{} :  {}'.format(username,message))

                    # Notifiy server that client will be close
                    command = 9
                    command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                    # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
                    message = "User close"
                    message = message.encode('utf-8')
                    message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                    client_socket.send(command_header + message_header + message)
                    client_socket.close()
                    print("Adios")
                    os._exit(0)
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                break

            continue
        
        except KeyboardInterrupt as e :
            print("connection close")
            send_last_msg = True
            os._exit(0)
            break
        
        except ValueError as e :
            print("Server closed")
            print("Adios")
            os._exit(0)
            break
        
        
        except Exception as e :
            _, _, tb = sys.exc_info()
            print('file name = ', __file__)
            print('error line No = {}'.format(tb.tb_lineno))
            print(e)
            print("thread exception") 
            print("Adios")
            os._exit(0)

def main() :
    try :
        # Start thread that print message
        start_new_thread(threaded,())


        while (True):
            # Wait for user command
            message = input()

            # If message is not empty - send it
            if message:

                # command detect
                if message[0] == '\\' :
                    parse_list = message.split(" ")
                    _command = parse_list[0]

                    # \users command 
                    if _command == '\\users' :
                        command = 1
                        command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                        message = "dum" 
                        message = message.encode('utf-8')
                        message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                        client_socket.send(command_header+message_header+message)

                    # whispering command
                    elif _command == '\\wh' :
                        if len(parse_list) < 3 :
                            print("Enter \\wh <nickname> <message>")
                        else :
                            command = 2
                            username = parse_list[1].encode('utf-8')
                            message = " ".join(parse_list[2:]).encode('utf-8')
                            
                            command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                            username_header = "{:<{}}".format(len(username),HEADER_LENGTH).encode('utf-8')
                            client_socket.send(command_header+username_header+username)

                            message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                            client_socket.send(command_header + message_header + message)
                    # exit command
                    elif _command == '\\exit' :
                        command = 9
                        command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                        # Send message to server that client will be closed
                        message = "User close"
                        message = message.encode('utf-8')
                        message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                        client_socket.send(command_header + message_header + message)
                        client_socket.close()
                        print("adios~")
                        os._exit(0)
                    
                    # version check command
                    elif _command == '\\version' :
                        command = 4
                        command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                        message = CLIENT_VERSION
                        message = message.encode('utf-8')
                        message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                        client_socket.send(command_header+message_header+message)


                    # rename command. server will judge that new nickname is valid
                    elif _command == '\\rename' :
                        command = 5
                        if len(parse_list) < 2 :
                            print("Enter \\rename <nickname>")

                        command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                        message = " ".join(parse_list[1:]).encode('utf-8')
                        message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                        client_socket.send(command_header+message_header+message)

                    # Check rtt command
                    elif _command == '\\rtt' :
                        command = 6
                        command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                        message = "RTT time check".encode('utf-8')
                        message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                        sent_time = datetime.datetime.now()
                        client_socket.send(command_header+message_header+message)
                    elif _command == '\\fsend' :
                        command = 7
                        command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                        message = " ".join(parse_list[1:]).encode('utf-8')
                        print("Sending file name check : ",message.decode("utf-8"))
                        message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                        print("Sending file name header check : ",message_header.decode("utf-8"))

                        file_name = message.decode('utf-8')
                        if os.path.exists(file_name) :
                            with open(file_name,'rb') as file :
                                file_data = file.read()
                            if len(file_data) > 5*1024*1024 :
                                print("File size exceeds 5MB. Canceled")
                            else :
                                file_header = "{:<{}}".format(len(file_data),F_HEADER_LENGTH).encode('utf-8')
                                print(file_header.decode('utf-8'))
                                file_length = file_header.decode('utf-8')
                                info = command_header + message_header + message + file_header
                                client_socket.send(info)
                                #client_socket.send(command_header+message_header+message+file_header)
                                BUFF_SIZE = 4096
                                while (len(file_data) > BUFF_SIZE) :
                                    client_socket.send(file_data[:4096])
                                    file_data = file_data[BUFF_SIZE:]
                                client_socket.send(file_data)


                                print("fsend message sent")

                        else :
                            print("file '{}' is not exists".format(file_name))
                    elif _command == '\\wsend' :
                        command = 8 
                        command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                        username = parse_list[1].encode('utf-8')
                        username_header = "{:<{}}".format(len(username),HEADER_LENGTH).encode('utf-8')
                        
                        message = " ".join(parse_list[2:]).encode('utf-8')
                        print("Sending file name check : ",message.decode("utf-8"))
                        message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                        print("Sending file name header check : ",message_header.decode("utf-8"))

                        file_name = message.decode('utf-8')
                        if os.path.exists(file_name) :
                            with open(file_name,'rb') as file :
                                file_data = file.read()
                            if len(file_data) > 5*1024*1024 :
                                print("File size exceeds 5MB. Canceled")
                            else :
                                file_header = "{:<{}}".format(len(file_data),F_HEADER_LENGTH).encode('utf-8')
                                print("file_header check : {}".format(file_header.decode('utf-8')))
                                info = command_header + username_header+username+message_header+message + file_header
                                client_socket.send(info) 
                                
                                BUFF_SIZE = 4096
                                while (len(file_data) > BUFF_SIZE) :
                                    client_socket.send(file_data[:4096])
                                    file_data = file_data[BUFF_SIZE:]
                                client_socket.send(file_data)
                                print("wsend message sent")

                        else :
                            print("file '{}' is not exists".format(file_name))




                # With not involves all cases above, it is normal chat message
                else :
                    command = 0
                    command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
                    print("message debug :",message)
                    message = message.encode('utf-8')
                    message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
                    client_socket.send(command_header + message_header + message)

    
    # Ctrl + C command
    except KeyboardInterrupt as e :

        # Notify server that client will be close
        print("connection close")
        command = 9
        command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
        message = "User close"
        message = message.encode('utf-8')
        message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
        client_socket.send(command_header + message_header + message)
        client_socket.close()
        print("adios~")
        os._exit(0)

    # This case is already handled in above 
    except SystemExit :
        None
   
    '''
    except Exception as e :
        _, _, tb = sys.exc_info()
        print('file name = ', __file__)
        print('error line No = {}'.format(tb.tb_lineno))
        print(e)
        print("Every exception taken") 
        print("Adios")
        os._exit(0)
    '''

    # send  message to server that contains 'client will be close'
    command = 9
    command_header = "{:<{}}".format(command,C_HEADER_LENGTH).encode('utf-8')
    message = "User close"
    message = message.encode('utf-8')
    message_header = "{:<{}}".format(len(message),HEADER_LENGTH).encode('utf-8')
    client_socket.send(command_header + message_header + message)
    client_socket.close()

    client_socket.close()
    print("adios~")



if __name__ == "__main__" :
    main()
















