import socket
import threading
import json
import os

def encode(message):
    return (json.dumps(message) + "\n").encode()

def decode(message):
    return json.loads(message.decode())

def broadcast_message(message_type, message, clients):
    disconnected_users = []
    for user in list(clients.keys()):
        try:
            user.send(encode({"type": message_type, "message": message}))
        except (ConnectionError, ConnectionAbortedError, BrokenPipeError, ConnectionResetError, ConnectionResetError):
            user.close()
            disconnected_users.append(user)

        for dead_user in disconnected_users:
            name = clients.get(dead_user, "Unknown")
            if dead_user in clients:
                del clients[dead_user]

            for client in list(clients.keys()):
                try:
                    client.send(encode({"type": "chat", "message": f"{name} left the chat"}))
                except:
                    pass  # ignore errors
def kick_client(client):
    if client in clients:
        client.close()
        del clients[client]

def handle_messages(client, address):
    try:
        name_data = decode(client.recv(1024))
        if name_data["type"] == "name":
            name = name_data["message"]
            clients[client] = name
            broadcast_message("users", list(clients.values()), clients)
            broadcast_message("chat", f"{name} joined the chat", clients)
        while True:
            client_response = decode(client.recv(1024))
            if client_response["type"] == "chat":
                broadcast_message("chat", f"{name}: {client_response['message']}", clients)
            if client_response["type"] == "kick":
                kicked_client = None
                kick_client(kicked_client)
    except (ConnectionError, ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
        del clients[client]
        client.close()
        broadcast_message("users", list(clients.values()), clients)
        broadcast_message("chat", f"{name} left the chat", clients)


if __name__ == "__main__":

    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 9999))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind(('0.0.0.0', port))
    server.listen(3)

    clients = {}

    while True:

        client, address, = server.accept()
        thread = threading.Thread(target=handle_messages, args=(client, address), daemon=True)
        thread.start()