import socket
import threading
import customtkinter
from tkinter import messagebox
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("192.168.1.104", 9999))

class CreateLoginWindow(customtkinter.CTk):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.geometry("200x200")
        self.name_entry = customtkinter.CTkEntry(self)
        self.name_entry.place(relx=0.5, rely=0.3, anchor="center")
        self.submit_button = customtkinter.CTkButton(self, text="submit", command=self.submit_button_callback)
        self.submit_button.place(relx=0.5, rely=0.5, anchor="center")

    def submit_button_callback(self):
        name = self.name_entry.get()
        if name.strip():
            self.client.send(name.encode())
            self.submit_button.configure(state="disabled")
            self.quit()
        else:
            messagebox.showerror(message="please ")
class App(customtkinter.CTk):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.geometry("800x600")

        self.frame = customtkinter.CTkScrollableFrame(self)
        self.frame.place(rely=0.05, relx=0.5, anchor="n", relheight=0.7, relwidth=0.8)

        self.my_font = customtkinter.CTkFont(family="Arial", size=16, weight="normal")
        self.entry = customtkinter.CTkEntry(self, font=self.my_font)
        self.entry.place(rely=0.9, relx=0.5, anchor="center", relwidth=0.8, relheight=0.05)
        self.entry.bind("<Return>", self.on_enter)

        threading.Thread(target=self.get_message).start()

    def on_enter(self, event=None):
        message = self.entry.get()
        self.entry.delete(0, "end")
        self.send_message(message)

    def get_message(self):
        while True:
            message = self.client.recv(1024).decode()
            label = customtkinter.CTkLabel(self.frame, text=message, font=self.my_font)
            label.pack(anchor="w")


    def send_message(self, message):
        if message is not None:
            self.client.send(message.encode())

if __name__ == "__main__":
    login_window = CreateLoginWindow(client)
    login_window.mainloop()
    login_window.destroy()

    app = App(client)
    app.mainloop()