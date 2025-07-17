import socket
import threading


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("192.168.1.104", 9999))
server.listen(3)
clients = {}

def handle_messages(client, address):
    print(f"[NEW CLIENT] {address}, connected")
    name = client.recv(1024).decode()
    clients[client] = name
    print(clients)

    while True:
        client_response = client.recv(1024).decode()
        for user in clients.keys():
            user.send(f"{name}: {client_response}".encode())

while True:
    client, address, = server.accept()
    thread = threading.Thread(target=handle_messages, args=(client, address))
    thread.start()