import socket
import os

HEADER = 1024
PORT = 5050
FORMAT = 'utf-8'
DISCONNECTMESSAGE = "***!DISCONNECT!***"
SERVER = "192.168.1.217"
ADDR = (SERVER,PORT)

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(ADDR)

def sendFile(path):
    fileName = os.path.basename(path).encode(FORMAT)
    fileName += b' ' * (100 - len(fileName))
    fileLength = str(os.path.getsize(fileName)).encode(FORMAT)
    fileLength += b' ' * (HEADER - len(fileLength))
    
    client.send(fileName)
    client.send(fileLength)
    
    fileData = ""
    with open(path,'rb') as file:
        while len(fileData) < int(fileLength):
            fileData = file.read(HEADER)
            fileData += b' ' * (HEADER - len(fileData))
            client.send(fileData)
            
    
path = "H:/Programming/python/Course/Projects/ClientServerFilesSharingProject/Client.py"
sendFile(path)


