import socket
import os
import tkinter as tk
from tkinter import filedialog, ttk

HEADER = 1024
PORT = 5050
FORMAT = 'utf-8'
SERVER = "192.168.1.217"  # Change this to your server's IP address
ADDR = (SERVER, PORT)
CLOUD_FOLDER = "H:/Programming/python/Course/Projects/ClientServerFilesSharingProject/CloudFolder"
DISCONNECTMESSAGE = "***!DISCONNECT!***"

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Client")
        self.root.geometry("600x400")
        self.root.configure(bg="#e0f7fa")

        # Frame for directory listing and buttons
        self.frame = tk.Frame(self.root, bg="#ffffff", bd=2, relief=tk.RAISED)
        self.frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Directory listing
        self.tree = ttk.Treeview(self.frame, columns=("Name",), show='tree')
        self.tree.heading("#0", text="Files in Cloud Folder")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Log area
        self.log_text = tk.Text(self.frame, wrap=tk.WORD, height=5, bg="#f1f8e9", font=('Arial', 12))
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Buttons
        button_style = {'bg': '#00796b', 'fg': 'white', 'font': ('Arial', 12), 'width': 20}
        self.select_file_button = tk.Button(self.frame, text="Select File to Send", command=self.select_file, **button_style)
        self.select_file_button.pack(pady=5, side=tk.LEFT, padx=5)
        
        self.send_button = tk.Button(self.frame, text="Send File to Server", command=self.send_file, **button_style)
        self.send_button.pack(pady=5, side=tk.LEFT, padx=5)

        # Initialize connection
        self.client_socket = None
        self.file_path = None
        self.connect_to_server()
        self.auto_refresh()

    def connect_to_server(self):
        """Attempt to connect to the server and handle errors."""
        if self.client_socket:
            self.client_socket.close()

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(10)
            self.client_socket.connect(ADDR)
            self.log_message("Connected to server.")
        except Exception as e:
            self.log_message(f"Error connecting to server: {e}")

    def refresh_directory(self):
        """Update the directory listing from the cloud folder."""
        self.tree.delete(*self.tree.get_children())
        for file_name in os.listdir(CLOUD_FOLDER):
            self.tree.insert("", tk.END, text=file_name)

    def select_file(self):
        """Open a file dialog to select a file to send."""
        local_file_path = filedialog.askopenfilename()
        if local_file_path:
            self.file_path = local_file_path
            self.log_message(f"Selected file: {self.file_path}")

    def send_file(self):
        """Send the selected file to the server."""
        if not self.file_path:
            self.log_message("No file selected.")
            return

        if not self.client_socket:
            self.log_message("Not connected to server.")
            return

        try:
            file_name = os.path.basename(self.file_path).encode(FORMAT)
            file_name += b' ' * (100 - len(file_name))
            file_length = str(os.path.getsize(self.file_path)).encode(FORMAT)
            file_length += b' ' * (HEADER - len(file_length))

            self.client_socket.send(file_name)
            self.client_socket.send(file_length)

            with open(self.file_path, 'rb') as file:
                while True:
                    file_data = file.read(HEADER)
                    if not file_data:
                        break
                    self.client_socket.send(file_data)

            self.client_socket.send(b'')  # Optional: Send an empty byte string to indicate end of file
            self.log_message("File sent to server successfully.")
        except Exception as e:
            self.log_message(f"Error sending file: {e}")

    def log_message(self, message):
        """Log messages to the GUI."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.yview(tk.END)

    def auto_refresh(self):
        """Auto-refresh the directory listing."""
        self.refresh_directory()
        self.root.after(5000, self.auto_refresh)  # Refresh every 5 seconds

    def on_closing(self):
        """Handle closing of the GUI."""
        if self.client_socket:
            try:
                self.client_socket.send(DISCONNECTMESSAGE.encode(FORMAT))
                self.client_socket.close()
                self.log_message(f"Disconnected from server at {ADDR}.")
            except Exception as e:
                self.log_message(f"Error disconnecting from server: {e}")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
