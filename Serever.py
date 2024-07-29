import socket
import threading
import os

HEADER = 1024
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER,PORT)
FORMAT = 'utf-8'
DISCONNECTMESSAGE = "***!DISCONNECT!***"
PATH = "H:/Programming/python/Course/Projects/ClientServerFilesSharingProject/CloudFolder"

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(ADDR)



def handleClient(conn,addr):
    print(f"[NEW CONNECTIONS] {addr} connected")
    
    connected = True
    while connected:
        
        fileName = conn.recv(100).decode(FORMAT)
        if fileName:
            if fileName == DISCONNECTMESSAGE:
                connected = False
                
            with open(f"{PATH}/{fileName}",'w') as file:
                dataLength = conn.recv(HEADER).decode(FORMAT)
                if dataLength:
                    fileData = ""
                    while len(fileData) < int(dataLength):
                        fileData += conn.recv(HEADER).decode(FORMAT)
                    file.write(fileData)

            conn.send("MSG Received".encode(FORMAT))
        
    conn.close()

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn,addr = server.accept()
        thread = threading.Thread(target=handleClient,args=(conn,addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print("[STARTING] server is starting...")
start()
        