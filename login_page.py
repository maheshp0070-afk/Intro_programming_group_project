import tkinter as tk
from tkinter import ttk, messagebox
import logging
from admin_GUI import AdminPage
from admin_logic import *

class LoginPage(tk.Frame):
    def __init__(self, App):
        super().__init__(App)
        self.canvas = tk.Canvas(self, width = 1280, height = 720)
        self.canvas.pack(expand=True, fill="both")

        # Adds Background Photo
        self.bg = tk.PhotoImage(file="Desert.png")
        self.canvas_bg = self.canvas.create_image(0, 0, image=self.bg, anchor="nw")

        #Username and Password
        title_label = tk.Label(self, text = "CampTrack Login Page", font = ("Comic Sans MS", 20), bg= "white")
        u_label = tk.Label(self.canvas, text = "Enter your login: ", font = ("Comic Sans MS", 20), bg= "white")
        p_label = tk.Label(self.canvas, text="Enter your password: ", font = ("Comic Sans MS", 20), bg= "white")
        login_button = ttk.Button(self.canvas, text="Login", command=self.login_)

        self.login = ttk.Entry(self.canvas, width=40, font = ("Comic Sans MS", 20), validate="key", validatecommand = (self.register(lambda x: len(x)<20), '%P'))
        self.password = ttk.Entry(self.canvas, width=40, show="*", font = ("Comic Sans MS", 20), validate="key", validatecommand = (self.register(lambda x: len(x)<20), '%P'))

        self.canvas.create_window(640, 200, window = title_label)
        self.canvas.create_window(640, 250, window = u_label)
        self.canvas.create_window(640, 340, window = p_label)
        self.canvas.create_window(640, 290, window = self.login)
        self.canvas.create_window(640, 380, window = self.password)
        self.canvas.create_window(640, 420, window = login_button)


    def login_(self):
        username = self.login.get()
        password = self.password.get()
        users = UserManager.load_users()


        #Check username and password is in database
        if username not in users["username"].values:
            messagebox.showerror("Error", "Incorrect username or password")
            return

        user_row = users[users["username"] == username].iloc[0]
        role = user_row["role"]
        status = user_row["status"]

        if role == "admin":
            logging.info("Admin Logged In")
            self.destroy()
            admin_window = AdminPage(self.master)
            admin_window.pack(fill = "both", expand = True)
        if status == True:
            if role == "coordinator":
                logging.info("Logistics Coordinator Logged In")
                self.destroy()
                import CoordinatorDashboard
                pass
            if role == "leader":
                logging.info(f"{self.username} Logged In")
                pass
        elif status == False:
            messagebox.showerror("Error", "User is disabled.")

if __name__ == '__main__':
    root = tk.Tk()
    app = LoginPage(root)
    root.geometry("1280x720")
    root.resizable(False, False)
    app.pack(fill = "both", expand = True)
    app.mainloop()
