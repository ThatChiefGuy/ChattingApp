import socket
import threading
import customtkinter
import json
from tkinter import messagebox
import os

port = int(os.environ.get("PORT", 9999))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("192.168.1.103", port))

def encode(message):
    return (json.dumps(message) + "\n").encode()


class CreateLoginWindow(customtkinter.CTk):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.geometry("200x200")
        self.name_entry = customtkinter.CTkEntry(self)
        self.name_entry.bind("<Return>", self.submit_button_callback)
        self.name_entry.place(relx=0.5, rely=0.3, anchor="center")
        self.submit_button = customtkinter.CTkButton(self, text="submit", command=self.submit_button_callback)
        self.submit_button.place(relx=0.5, rely=0.5, anchor="center")

    def submit_button_callback(self, event=None):
        name = {"type":"name", "message":self.name_entry.get()}
        if name["message"].strip():
            self.client.send(encode(name))
            self.submit_button.configure(state="disabled")
            self.quit()
        else:
            messagebox.showerror(message="please enter a name")

class App(customtkinter.CTk):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.geometry("800x600")
        self.protocol("WM_DELETE_WINDOW", self.on_closign)
        self.chat_frame = customtkinter.CTkScrollableFrame(self)
        self.chat_frame.place(rely=0.05, relx=0.25, anchor="nw", relheight=0.8, relwidth=0.7)

        self.my_font = customtkinter.CTkFont(family="Arial", size=16, weight="normal")
        self.entry = customtkinter.CTkEntry(self, font=self.my_font)
        self.entry.place(rely=0.9, relx=0.25, anchor="w", relwidth=0.6, relheight=0.05)
        self.entry.bind("<Return>", self.send_and_clear)

        self.send_button = customtkinter.CTkButton(self, font=self.my_font, text="send", command=self.send_and_clear)
        self.send_button.place(rely=0.90, relx=0.9, relwidth=0.1, relheight=0.05, anchor="center")

        self.online_frame = customtkinter.CTkScrollableFrame(self)
        self.online_frame.place(rely=0.1, relx=0.025, anchor="nw", relheight=0.85, relwidth=0.2)
        self.online_users_label = customtkinter.CTkLabel(self, text="Online users", font=("Arial", 20))
        self.online_users_label.place(rely=0.05, relx=0.025, anchor="nw")
        threading.Thread(target=self.get_message, daemon=True).start()

    def send_and_clear(self, event=None):
        message = {"type":"chat", "message": self.entry.get()}
        self.entry.delete(0, "end")
        self.send_message(message)

    def on_closign(self):
        try:
            client.close()
        except:
            pass
        self.destroy()

    def get_message(self):
        buffer = ""
        while True:
            try:
                message_data = self.client.recv(1024).decode()
                buffer += message_data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        message_data = json.loads(line)

                        self.handle_messages(message_data)
            except (ConnectionAbortedError, ConnectionResetError, ConnectionError):
                break
            except json.JSONDecodeError:
                # Handle or ignore malformed data (optional)
                pass
    def send_message(self, message_data):
        if message_data is not None:
            self.client.send(encode(message_data))


    def handle_messages(self, message_data):
        if message_data["type"] == "users":
            for widget in self.online_frame.winfo_children():
                widget.destroy()
            for name in message_data["message"]:
                label = customtkinter.CTkLabel(self.online_frame, text=name, font=self.my_font,
                                               wraplength=600, justify="left")
                label.pack(anchor="w")
        if message_data["type"] == "chat":
            label = customtkinter.CTkLabel(self.chat_frame, text=message_data["message"], font=self.my_font,
                                           wraplength=600, justify="left")
            label.pack(anchor="w")

if __name__ == "__main__":
    login_window = CreateLoginWindow(client)
    login_window.mainloop()
    login_window.destroy()

    app = App(client)
    app.mainloop()