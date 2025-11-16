import tkinter as tk
from tkinter import ttk, messagebox
import logging
from Adminpage import adminpage
import json


class loginpage(tk.Frame):
    def __init__(self, App, controller):
        super().__init__(App)
        self.controller = controller
        ttk.Label(self, text="CampTrack Login Page", font=("Arial", 20)).pack()
        ttk.Label(self, text="Enter your login: ").pack()
        self.login = ttk.Entry(self, width=40)
        self.login.pack()

        ttk.Label(self, text="Enter your password: ").pack()
        self.password = ttk.Entry(self, width=40, show="*")
        self.password.pack()

        ttk.Button(self, text="Login", command=self.login_).pack()

    def login_(self):
        with open("users_database.json", 'r') as file:
            users = json.load(file)

        user = self.login.get()
        password = self.password.get()
        if user not in users:
            messagebox.showerror("Error", "User not found")

        if users[user]["Password"] != password:
            messagebox.showerror("Error", "Incorrect Password")

        role = users[user]["Role"]

        if role == "Admin":
            logging.info("Admin Logged In")
            self.controller.show_frame(adminpage)
        if role == "Logistics Co-ordinator":
            logging.info("Logistics Co-ordinator Logged In")
            pass


if __name__ == '__main__':
    root = tk.Tk()
    app = loginpage(root, root)
    app.pack()
    app.mainloop()