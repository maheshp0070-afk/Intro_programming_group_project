import tkinter as tk
from tkinter import ttk, messagebox
import logging
from admin_GUI import AdminPage
import pandas as pd

class loginpage(tk.Frame):
    def __init__(self, App, controller):
        super().__init__(App)
        self.controller = controller
        ttk.Label(self, text = "CampTrack Login Page", font = ("Arial", 20)).pack()
        ttk.Label(self, text = "Enter your login: ").pack()
        self.login = ttk.Entry(self, width = 40)
        self.login.pack()

        ttk.Label(self, text = "Enter your password: ").pack()
        self.password = ttk.Entry(self, width = 40, show = "*")
        self.password.pack()

        ttk.Button(self, text="Login", command=self.login_).pack()

    def login_(self):
        with open("data/users_database.csv", 'r') as file:
            users = pd.read_csv(file)

        user = self.login.get()
        password = self.password.get()

        #Check username and password is in database
        if user not in users["Username"].tolist() or users.loc[user, "Password"] != password :
            messagebox.showerror("Error", "Incorrect username or password")
            return

        role = users.loc[user, "Role"]

        if role == "Admin":
            logging.info("Admin Logged In")
            self.controller.show_frame(AdminPage)
        #if role == "Logistics Co-ordinator":
            #logging.info("Logistics Co-ordinator Logged In")
            #pass

if __name__ == '__main__':
    root = tk.Tk()
    app = loginpage(root, root)
    app.pack()
    app.mainloop()