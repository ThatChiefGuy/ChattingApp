import socket
import threading
import json

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("192.168.1.100", 9999))
server.listen(3)
clients = {}

def encode(message):
    return json.dumps(message).encode()

def decode(message):
    return json.loads(message.decode())

def handle_messages(client, address):
    print(f"[NEW CLIENT] {address}, connected")
    name_data = decode(client.recv(1024))
    if name_data["type"] == "name":
        name = name_data["message"]
        clients[client] = name

    while True:
        client_response = decode(client.recv(1024))
        if client_response["type"] == "chat":
            for user in clients.keys():
                user.send(encode({"type":"chat","message":f"{name}: {client_response['message']}"}))

while True:
    client, address, = server.accept()
    thread = threading.Thread(target=handle_messages, args=(client, address))
    thread.start()