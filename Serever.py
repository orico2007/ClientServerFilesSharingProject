import socket
import threading

HEADER = 64
PORT = 5050

SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER,PORT)

FORMAT = 'utf-8'

DISCONNECTMESSAGE = "***!DISCONNECT!***"

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(ADDR)

def handleClient(conn,addr):
    print(f"[NEW CONNECTIONS] {addr} connected")
    
    connected = True
    while connected:
        msgLeangth = conn.recv(HEADER).decode(FORMAT)
        msgLeangth = int(msgLeangth)
        msg = conn.recv(msgLeangth).decode(FORMAT)
        if msg == DISCONNECTMESSAGE:
            connected = False
        
        print(f'[{addr}] {msg}')
        
    conn.close()

def start():
    server.listen()
    print(f"[LISTENING Server is listening on {SERVER}")
    while True:
        conn,addr = server.accept()
        thread = threading.Thread(target=handleClient,args=(conn,addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

print("[STARTING] server is startting...")
start()
        