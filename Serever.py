import socket
import threading
import os
import tkinter as tk
from tkinter import ttk

HEADER = 1024
PORT = 5050
FORMAT = 'utf-8'
DISCONNECTMESSAGE = "***!DISCONNECT!***"
PATH = "H:/Programming/python/Course/Projects/ClientServerFilesSharingProject/CloudFolder"

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Server")
        self.root.geometry("600x400")
        self.root.configure(bg="#e0f2f1")

        # Frame for text area and directory listing
        self.frame = tk.Frame(self.root, bg="#ffffff", bd=2, relief=tk.RAISED)
        self.frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Text area for logs
        self.text_area = tk.Text(self.frame, wrap=tk.WORD, height=5, bg="#f1f8e9", font=('Arial', 12))
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Directory listing
        self.tree = ttk.Treeview(self.frame, columns=("Name",), show='tree')
        self.tree.heading("#0", text="Files in Cloud Folder")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.refresh_directory()

        # Start Server Button
        button_style = {'bg': '#00796b', 'fg': 'white', 'font': ('Arial', 12), 'width': 20}
        self.start_button = tk.Button(self.frame, text="Start Server", command=self.start_server, **button_style)
        self.start_button.pack(pady=5)

        # Initialize server
        self.server_socket = None

    def start_server(self):
        """Start the server and listen for incoming connections."""
        if self.server_socket:
            self.log_message("Server is already running.")
            return

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', PORT))
        self.server_socket.listen()
        self.log_message("Server is listening for connections...")

        # Start a new thread to accept connections
        server_thread = threading.Thread(target=self.accept_connections)
        server_thread.daemon = True
        server_thread.start()

    def accept_connections(self):
        """Accept and handle incoming client connections."""
        while True:
            try:
                conn, addr = self.server_socket.accept()
                self.log_message(f"[NEW CONNECTION] {addr} connected")
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                self.log_message(f"Accept connection error: {e}")

    def handle_client(self, conn, addr):
        """Handle file transfer from a client."""
        while True:
            try:
                file_name = conn.recv(100).decode(FORMAT).strip()
                if file_name == DISCONNECTMESSAGE:
                    self.log_message(f"Client {addr} disconnected.")
                    break
                self.log_message(f"Receiving file: {file_name}")
                with open(f"{PATH}/{file_name}", 'wb') as file:
                    data_length = int(conn.recv(HEADER).decode(FORMAT).strip())
                    received = 0
                    while received < data_length:
                        file_data = conn.recv(HEADER)
                        if not file_data:
                            break
                        file.write(file_data)
                        received += len(file_data)
                self.log_message(f"File {file_name} received successfully.")
                self.refresh_directory()
            except Exception as e:
                self.log_message(f"Error: {e}")
                break
        conn.close()  # Close the connection after handling

    def refresh_directory(self):
        """Update the directory listing from the cloud folder."""
        self.tree.delete(*self.tree.get_children())
        for file_name in os.listdir(PATH):
            self.tree.insert("", tk.END, text=file_name)

    def log_message(self, message):
        """Log messages to the GUI."""
        self.text_area.insert(tk.END, f"{message}\n")
        self.text_area.yview(tk.END)

    def on_closing(self):
        """Handle closing of the GUI."""
        if self.server_socket:
            self.log_message("Server is shutting down...")
            self.server_socket.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
