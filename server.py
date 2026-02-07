import socket
import threading
import os
from datetime import datetime

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.users_file = "server_storage/users.txt"
        self.clients = {}  # username -> socket

        # Ensure storage folder exists
        os.makedirs("server_storage", exist_ok=True)

    # ---------- USER MANAGEMENT ----------
    def load_users(self):
        if not os.path.exists(self.users_file):
            return set()
        with open(self.users_file, "r") as f:
            return set(line.strip() for line in f)

    def save_user(self, username):
        users = self.load_users()
        if username not in users:
            with open(self.users_file, "a") as f:
                f.write(username + "\n")

    def broadcast_users(self):
        user_list = ",".join(self.clients.keys())
        for sock in self.clients.values():
            try:
                sock.send(f"USERS:{user_list}".encode())
            except:
                pass

    # ---------- CLIENT HANDLER ----------
    def handle_client(self, sock, username):
        while True:
            try:
                data = sock.recv(4096)
                if not data:
                    break

                # Make sure the data has the separator
                if b"|" not in data:
                    continue

                target, encrypted_msg = data.split(b"|", 1)
                target = target.decode()

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # ----- STORE MESSAGE ENCRYPTED -----
                log_file = f"server_storage/{target}_log.txt"
                with open(log_file, "a") as f:
                    f.write(f"[{timestamp}] {username} -> {target}: {encrypted_msg.decode()}\n")

                # ----- FORWARD TO TARGET IF ONLINE -----
                if target in self.clients:
                    try:
                        self.clients[target].send(username.encode() + b"|" + encrypted_msg)
                    except:
                        pass
                else:
                    sock.send(b"SERVER|User offline or not found")

            except Exception as e:
                print(f"[!] Error with {username}: {e}")
                break

        # Clean up on disconnect
        sock.close()
        if username in self.clients:
            del self.clients[username]
        self.broadcast_users()
        print(f"[-] {username} disconnected")

    # ---------- SERVER START ----------
    def start(self):
        server = socket.socket()
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen()

        print("✅ Secure Message Chat System Server running")

        while True:
            client_socket, _ = server.accept()
            try:
                username = client_socket.recv(1024).decode()
            except:
                client_socket.close()
                continue

            self.save_user(username)
            self.clients[username] = client_socket
            self.broadcast_users()

            print(f"[+] {username} connected")

            threading.Thread(
                target=self.handle_client,
                args=(client_socket, username),
                daemon=True
            ).start()


if __name__ == "__main__":
    server = ChatServer("127.0.0.1", 5555)
    server.start()
