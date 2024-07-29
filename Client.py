import socket
import os
import tkinter as tk
from tkinter import filedialog, ttk, simpledialog
from tkinter import messagebox

HEADER = 1024
PORT = 5050
FORMAT = 'utf-8'
SERVER = "192.168.1.217"  # Change this to your server's IP address
ADDR = (SERVER, PORT)
DISCONNECTMESSAGE = "***!DISCONNECT!***"
LISTCOMMAND = "***!LIST!***"
MKDIRCOMMAND = "***!MKDIR!***"

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Client")
        self.root.geometry("800x600")
        self.root.configure(bg="#f5f5f5")

        self.frame = tk.Frame(self.root, bg="#ffffff", bd=2, relief=tk.RAISED)
        self.frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Style configuration
        style = ttk.Style()
        style.configure("Treeview", background="#ffffff", foreground="#000000", font=('Arial', 12))
        style.configure("Treeview.Heading", font=('Arial', 14, 'bold'))
        style.configure("TButton", font=('Arial', 12, 'bold'), padding=10)
        style.configure("TFrame", background="#f5f5f5")

        # Directory listing
        self.tree = ttk.Treeview(self.frame, columns=("Name",), show='tree', selectmode="browse")
        self.tree.heading("#0", text="Files and Folders")
        self.tree.bind('<Double-1>', self.on_treeview_double_click)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Log area
        self.log_text = tk.Text(self.frame, wrap=tk.WORD, height=5, bg="#e0f7fa", font=('Arial', 12))
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Buttons
        button_frame = tk.Frame(self.frame, bg="#ffffff")
        button_frame.pack(pady=5, fill=tk.X)

        button_style = {'bg': '#0288d1', 'fg': 'white', 'font': ('Arial', 12, 'bold'), 'width': 20}
        self.select_file_button = ttk.Button(button_frame, text="Select File to Send", command=self.select_file)
        self.select_file_button.pack(pady=5, side=tk.LEFT, padx=5)

        self.send_button = ttk.Button(button_frame, text="Send File to Server", command=self.send_file)
        self.send_button.pack(pady=5, side=tk.LEFT, padx=5)

        self.create_folder_button = ttk.Button(button_frame, text="Create Folder on Server", command=self.create_folder)
        self.create_folder_button.pack(pady=5, side=tk.LEFT, padx=5)

        self.back_button = ttk.Button(button_frame, text="Back", command=self.go_back)
        self.back_button.pack(pady=5, side=tk.LEFT, padx=5)

        self.client_socket = None
        self.current_path = ""
        self.path_stack = []

        self.connect_to_server()

    def connect_to_server(self):
        """Connect to the server."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(ADDR)
            self.refresh_directory()
        except Exception as e:
            self.log_message(f"Connection error: {e}")

    def select_file(self):
        """Open a file dialog to select a file."""
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_to_send = file_path
            self.log_message(f"Selected file: {file_path}")

    def send_file(self):
        """Send the selected file to the server."""
        if not hasattr(self, 'file_to_send'):
            self.log_message("No file selected to send.")
            return

        try:
            file_name = os.path.basename(self.file_to_send)
            self.client_socket.send(file_name.encode(FORMAT))

            with open(self.file_to_send, 'rb') as file:
                data = file.read()
                self.client_socket.send(str(len(data)).encode(FORMAT))
                self.client_socket.send(data)
            self.log_message(f"File {file_name} sent successfully.")
        except Exception as e:
            self.log_message(f"Error sending file: {e}")

    def create_folder(self):
        """Prompt the user for a folder name and send the request to the server."""
        folder_name = simpledialog.askstring("Create Folder", "Enter folder name:")
        if folder_name:
            try:
                self.client_socket.send(f"{MKDIRCOMMAND}:{folder_name}".encode(FORMAT))
                self.log_message(f"Requesting to create folder: {folder_name}")
                self.refresh_directory()
            except Exception as e:
                self.log_message(f"Error creating folder: {e}")

    def refresh_directory(self):
        """Request and refresh directory listing."""
        if not self.client_socket:
            self.log_message("Not connected to server.")
            return

        try:
            list_command = f"{LISTCOMMAND}:{self.current_path}".encode(FORMAT)
            self.client_socket.send(list_command)
            dir_listing = self.client_socket.recv(HEADER).decode(FORMAT)
            self.update_directory_tree(eval(dir_listing))
        except Exception as e:
            self.log_message(f"Error refreshing directory: {e}")

    def update_directory_tree(self, dir_listing):
        """Update the Treeview with the directory listing."""
        self.tree.delete(*self.tree.get_children())
        for item in dir_listing:
            self.tree.insert("", tk.END, text=item)

    def on_treeview_double_click(self, event):
        item = self.tree.selection()[0]
        selected_path = self.tree.item(item, "text")
        if selected_path.endswith('/'):
            self.path_stack.append(self.current_path)
            self.current_path = os.path.join(self.current_path, selected_path).replace("\\", "/")
            self.refresh_directory()

    def go_back(self):
        """Navigate to the previous directory."""
        if self.path_stack:
            self.current_path = self.path_stack.pop()
            self.refresh_directory()
        else:
            self.log_message("No previous directory to go back to.")

    def log_message(self, message):
        """Log messages to the GUI."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.yview(tk.END)

    def on_closing(self):
        """Handle closing of the GUI."""
        if self.client_socket:
            self.client_socket.send(DISCONNECTMESSAGE.encode(FORMAT))
            self.client_socket.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
