import socket
import threading
import tkinter as tk
from tkinter import simpledialog
from crypto_utils import CryptoManager

HOST = "127.0.0.1"
PORT = 5555


class ChatClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Secure Message Chat System")

        # User list
        self.users_list = tk.Listbox(self.root, width=20)
        self.users_list.pack(side="left", fill="y")
        self.users_list.bind("<<ListboxSelect>>", self.select_user)

        # Chat area
        self.chat_area = tk.Text(self.root, state="disabled")
        self.chat_area.pack(expand=True, fill="both")

        # Message entry
        self.entry = tk.Entry(self.root)
        self.entry.pack(fill="x")
        self.entry.bind("<Return>", self.send_message)

        # Network
        self.sock = socket.socket()
        self.sock.connect((HOST, PORT))

        # Login
        self.username = simpledialog.askstring("Login", "Enter username:")
        self.sock.send(self.username.encode())

        # Encryption setup
        with open("shared_key.txt", "r") as f:
            key_material = f.read().strip()
        self.crypto = CryptoManager(key_material)

        self.target_user = None

        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.root.mainloop()

    def select_user(self, event):
        if self.users_list.curselection():
            self.target_user = self.users_list.get(
                self.users_list.curselection()
            )
            self.display(f"🔐 Chatting with {self.target_user}")

    def receive_messages(self):
        while True:
            try:
                data = self.sock.recv(4096)

                if data.startswith(b"USERS:"):
                    users = data.decode().split(":")[1].split(",")
                    self.users_list.delete(0, tk.END)
                    for u in users:
                        if u != self.username:
                            self.users_list.insert(tk.END, u)
                else:
                    sender, encrypted = data.split(b"|", 1)
                    message = self.crypto.decrypt(encrypted)
                    self.display(f"[{sender.decode()}]: {message}")

            except:
                break

    def send_message(self, event=None):
        if self.target_user:
            msg = self.entry.get()
            encrypted = self.crypto.encrypt(msg)

            payload = self.target_user.encode() + b"|" + encrypted
            self.sock.send(payload)

            self.display(f"[You]: {msg}")
            self.entry.delete(0, tk.END)

    def display(self, msg):
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, msg + "\n")
        self.chat_area.config(state="disabled")
        self.chat_area.see(tk.END)


if __name__ == "__main__":
    ChatClient()