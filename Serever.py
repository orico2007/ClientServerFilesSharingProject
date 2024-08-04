import socket
import threading
import os
import tkinter as tk
from tkinter import ttk

HEADER = 1024
PORT = 5050
DISCONNECTMESSAGE = "***!DISCONNECT!***"
LISTCOMMAND = "***!LIST!***"
MKDIRCOMMAND = "***!MKDIR!***"
NAVIGATECOMMAND = "***!NAVIGATE!***"
DOWNLOADCOMMAND = "***!DOWNLOAD!***"
PATH = "H:/Programming/python/Course/Projects/ClientServerFilesSharingProject/CloudFolder"

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Server")
        self.root.geometry("800x600")
        self.root.configure(bg="#e0f2f1")

        self.frame = tk.Frame(self.root, bg="#ffffff", bd=2, relief=tk.RAISED)
        self.frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Style configuration
        style = ttk.Style()
        style.configure("Treeview", background="#ffffff", foreground="#000000", font=('Arial', 12))
        style.configure("Treeview.Heading", font=('Arial', 14, 'bold'))
        style.configure("TButton", font=('Arial', 12, 'bold'), padding=10)
        style.configure("TFrame", background="#e0f2f1")

        # Directory listing
        self.tree = ttk.Treeview(self.frame, columns=("Name",), show='tree')
        self.tree.heading("#0", text="Files in Cloud Folder")
        self.tree.bind('<Double-1>', self.on_treeview_double_click)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Log area
        self.text_area = tk.Text(self.frame, wrap=tk.WORD, height=5, bg="#f1f8e9", font=('Arial', 12))
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Buttons
        button_style = {'bg': '#0288d1', 'fg': 'white', 'font': ('Arial', 12, 'bold'), 'width': 20}
        self.start_button = tk.Button(self.frame, text="Start Server", command=self.start_server, **button_style)
        self.start_button.pack(pady=5)

        self.back_button = tk.Button(self.frame, text="Back", command=self.go_back, **button_style)
        self.back_button.pack(pady=5)

        # Initialize server
        self.server_socket = None
        self.current_path = PATH
        self.path_stack = []

        # Refresh the directory listing on startup
        self.refresh_directory()

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
        """Handle commands and file transfers from a client."""
        while True:
            try:
                command = conn.recv(HEADER).decode().strip()
                if command == DISCONNECTMESSAGE:
                    self.log_message(f"Client {addr} disconnected.")
                    break
                elif command.startswith(MKDIRCOMMAND):
                    folder_name = command.split(":")[1]
                    os.makedirs(os.path.join(self.current_path, folder_name), exist_ok=True)
                    self.log_message(f"Created folder: {folder_name}")
                    self.refresh_directory()
                elif command.startswith(LISTCOMMAND):
                    current_path = command.split(":")[1]
                    self.log_message(f"Listing directory: {current_path}")
                    dir_listing = self.get_directory_listing(current_path)
                    conn.send(";".join(dir_listing).encode())
                elif command.startswith(NAVIGATECOMMAND):
                    target_dir = command.split(":")[1]
                    new_path = os.path.join(self.current_path, target_dir)
                    if os.path.isdir(new_path):
                        self.path_stack.append(self.current_path)
                        self.current_path = new_path
                        self.refresh_directory()
                        conn.send("NAVIGATED".encode())
                    else:
                        conn.send("INVALID_DIRECTORY".encode())
                elif command.startswith(DOWNLOADCOMMAND):
                    file_name = command.split(":")[1]
                    file_path = os.path.join(self.current_path, file_name)
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        conn.send(f"{file_size}".encode())
                        with open(file_path, 'rb') as file:
                            while (chunk := file.read(HEADER)):
                                conn.send(chunk)
                        self.log_message(f"Sent file: {file_name}")
                    else:
                        conn.send("0".encode())
                else:
                    file_name = command
                    self.log_message(f"Receiving file: {file_name}")
                    file_size = int(conn.recv(HEADER).decode().strip())
                    with open(os.path.join(self.current_path, file_name), 'wb') as file:
                        data_received = 0
                        while data_received < file_size:
                            chunk = conn.recv(min(HEADER, file_size - data_received))
                            if not chunk:
                                break
                            file.write(chunk)
                            data_received += len(chunk)
                            self.log_message(f"Received {data_received}/{file_size} bytes")
                    self.log_message(f"File {file_name} received successfully.")
                    self.refresh_directory()
            except Exception as e:
                self.log_message(f"Error: {e}")
                break
        conn.close()

    def get_directory_listing(self, current_path):
        """Get a directory listing including subdirectories."""
        dir_listing = []
        full_path = os.path.join(PATH, current_path)
        for root, dirs, files in os.walk(full_path):
            for name in dirs:
                dir_listing.append(os.path.relpath(os.path.join(root, name), PATH) + '/')
            for name in files:
                dir_listing.append(os.path.relpath(os.path.join(root, name), PATH))
            break
        return dir_listing

    def refresh_directory(self):
        """Update the directory listing in the GUI."""
        self.tree.delete(*self.tree.get_children())
        for item in self.get_directory_listing(""):
            self.tree.insert("", tk.END, text=item)

    def go_back(self):
        """Navigate to the previous directory."""
        if self.path_stack:
            self.current_path = self.path_stack.pop()
            self.refresh_directory()
        else:
            self.log_message("No previous directory to go back to.")

    def log_message(self, message):
        """Log messages to the GUI."""
        self.text_area.insert(tk.END, f"{message}\n")
        self.text_area.yview(tk.END)

    def on_treeview_double_click(self, event):
        """Handle double-click on treeview item."""
        selected_item = self.tree.selection()
        if selected_item:
            dir_name = self.tree.item(selected_item)['text']
            if dir_name.endswith('/'):
                self.path_stack.append(self.current_path)
                self.current_path = os.path.join(self.current_path, dir_name)
                self.log_message(f"Navigated to {self.current_path}")
                self.refresh_directory()

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
