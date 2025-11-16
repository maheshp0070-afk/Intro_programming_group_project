import tkinter as tk
from tkinter import ttk, messagebox
import logging
from Adminpage import adminpage
import pickle

with open('users.pickle', 'rb') as file:
    user_list = pickle.load(file)

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
        user = self.login.get()
        password = self.password.get()
        if user == "Admin" and password == "Password":
            logging.info("Admin Logged In")
            self.controller.show_frame(adminpage)
            self.login.delete(0, tk.END)
            self.password.delete(0, tk.END)
        elif user in user_list and user_list[password]:
            messagebox.showinfo("Welcome", "Login Successful")
        else:
            logging.warning("Login Failed: Incorrect Username or Password")
            messagebox.showerror("Login Failed", "Incorrect Username or Password")

if __name__ == '__main__':
    root = tk.Tk()
    app = loginpage(root, root)
    app.pack()
    app.mainloop()