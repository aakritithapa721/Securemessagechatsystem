import socket
import threading
import os

HOST = "127.0.0.1"
PORT = 5555

USERS_FILE = "server_storage/users.txt"
clients = {}  # username -> socket


def load_users():
    if not os.path.exists(USERS_FILE):
        return set()
    with open(USERS_FILE, "r") as f:
        return set(line.strip() for line in f)


def save_user(username):
    users = load_users()
    if username not in users:
        os.makedirs("server_storage", exist_ok=True)
        with open(USERS_FILE, "a") as f:
            f.write(username + "\n")


def broadcast_users():
    user_list = ",".join(clients.keys())
    for sock in clients.values():
        sock.send(f"USERS:{user_list}".encode())


def handle_client(sock, username):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break

            target, encrypted_msg = data.split(b"|", 1)
            target = target.decode()

            if target in clients:
                clients[target].send(username.encode() + b"|" + encrypted_msg)
            else:
                sock.send(b"SERVER|User offline or not found")

        except:
            break

    sock.close()
    del clients[username]
    broadcast_users()
    print(f"[-] {username} disconnected")


def start():
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    print("✅ Secure Message Chat System Server running")

    while True:
        client_socket, _ = server.accept()
        username = client_socket.recv(1024).decode()

        save_user(username)
        clients[username] = client_socket
        broadcast_users()

        print(f"[+] {username} connected")

        threading.Thread(
            target=handle_client,
            args=(client_socket, username),
            daemon=True
        ).start()


if __name__ == "__main__":
    start()