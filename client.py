import socket
import threading
import tkinter as tk
from tkinter import simpledialog
from crypto_utils import CryptoManager
from chat_ui import ChatUI

HOST = "127.0.0.1"
PORT = 5555


class ChatClient:
    def __init__(self):
        # ----- NETWORK -----
        self.sock = socket.socket()
        self.sock.connect((HOST, PORT))

        # ----- LOGIN -----
        self.username = simpledialog.askstring("Login", "Enter username:")
        self.sock.send(self.username.encode())

        # ----- ENCRYPTION -----
        with open("shared_key.txt", "r") as f:
            key_material = f.read().strip()
        self.crypto = CryptoManager(key_material)

        # ----- UI -----
        self.root = tk.Tk()
        self.ui = ChatUI(self.root, self.username, self.send_to_server)

        # ----- THREAD -----
        threading.Thread(target=self.receive_messages, daemon=True).start()

        self.root.mainloop()

    # ---------- SEND ----------
    def send_to_server(self, target_user, msg):
        encrypted = self.crypto.encrypt(msg)
        payload = target_user.encode() + b"|" + encrypted
        self.sock.send(payload)

    # ---------- RECEIVE ----------
    def receive_messages(self):
        while True:
            try:
                data = self.sock.recv(4096)

                if data.startswith(b"USERS:"):
                    users = data.decode().split(":")[1].split(",")
                    self.root.after(0, lambda: self.ui.load_users(users))

                else:
                    sender, encrypted = data.split(b"|", 1)
                    message = self.crypto.decrypt(encrypted)
                    sender = sender.decode()
                    self.root.after(
                        0, lambda: self.ui.add_message(sender, message)
                    )

            except:
                break


if __name__ == "__main__":
    ChatClient()
