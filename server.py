import socket
import threading
import json

def encode(message):
    return (json.dumps(message) + "\n").encode()

def decode(message):
    return json.loads(message.decode())

def broadcast_message(message_type, message, clients):
    for user in list(clients.keys()):
        try:
            user.send(encode({"type": message_type, "message": message}))
        except ConnectionError:
            user.close()
            del clients[user]
            for user in clients:
                name = clients.get(user, "Unknown")
                user.close()
                for other_user in list(clients.keys()):
                    try:
                        other_user.send(encode({"type": "chat", "message": f"{name} left the chat"}))
                    except:
                        pass  # Optional: handle double-fail silently

def handle_messages(client, address):
    try:
        name_data = decode(client.recv(1024))
        if name_data["type"] == "name":
            name = name_data["message"]
            clients[client] = name
            client.send(encode({"type":"users", "message":list(clients.values())}))
            broadcast_message("chat", f"{name} joined the chat", clients)
        while True:
            client_response = decode(client.recv(1024))
            if client_response["type"] == "chat":
                broadcast_message("chat", f"{name}: {client_response['message']}", clients)
    except ConnectionError:
        del clients[client]
        client.close()
        broadcast_message("users", clients.values(), clients)
        print("leftuser ", name)


if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind(("192.168.1.144", 9999))
    server.listen(3)

    clients = {}

    while True:
        client, address, = server.accept()
        thread = threading.Thread(target=handle_messages, args=(client, address))
        thread.start()