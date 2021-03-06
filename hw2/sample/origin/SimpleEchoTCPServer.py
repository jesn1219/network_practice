#
# SimpleEchoTCPServer.py
#

from socket import *

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)

print("The server is ready to receive on port", serverPort)

while True:
    (connectionSocket, clientAddress) = serverSocket.accept()
    print('Connection requested from', clientAddress)
    message = connectionSocket.recv(2048)
    modifiedMessage = message.decode().upper()
    connectionSocket.send(modifiedMessage.encode())
    connectionSocket.close()

