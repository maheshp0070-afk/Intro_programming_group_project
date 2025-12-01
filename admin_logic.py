import logging, csv
from tkinter import *
import pandas as pd
from tkinter import messagebox

filepath = "data/users.csv"

class User:
    def __init__(self, username, password, role, is_active = True):
        self.username = username
        self.password = password
        self.role = role
        self.is_active = is_active

class UserManager:
    filepath = filepath

    @classmethod
    def load_users(cls):
        try:
            return pd.read_csv(cls.filepath)
        except FileNotFoundError:
            users = pd.DataFrame(columns = ["username", "password", "role", "status"])
            users.to_csv(filepath, index=False)

    @classmethod
    def create_user(cls, username, password, role, treeview):
        users = cls.load_users()
        users_list = users["username"].tolist()

        if username in users["username"].values:
            messagebox.showerror("Error", "User already exists")
            return

        if not username:
            messagebox.showerror("Error", "Username cannot be empty")

        if role == "Coordinator" and "Coordinator" in users["role"].values:
            messagebox.showerror("Error", "Only One Logistics Coordinator Allowed")
            return

        else:
            new_user = pd.DataFrame([{
                "username" : username,
                "password" : password,
                "role" : role,
                "status" : True}])
            new_user.to_csv(filepath, mode = 'a', index=False, header = False)
            logging.info(f"New User Created: {username}")
            messagebox.showinfo("Success", "New User has been added")
            treeview.insert("", 'end', values = (username, password, role, True))

    @classmethod
    def del_user(cls, username):
        users = cls.load_users()
        users = users[users["username"] != username]
        users.to_csv(filepath, index=False)
        logging.info(f"User Deleted: {username}")

    @classmethod
    def edit_user(cls, username, new_username, new_password):
        users = cls.load_users()
        selected_user = (users["username"] == username)
        users.loc[selected_user, "username"] = new_username
        users.loc[selected_user, "password"] = new_password
        users.to_csv(filepath, index=False)
        logging.info(f"Changed {username} to new username {new_username} and new password {new_password}")

    @classmethod
    def disable_account(cls,username):
        users = cls.load_users()
        users.loc[users["username"] == username, "is_active"] = False
        logging.info(f"User Disabled: {username}")
        users.to_csv(filepath, index=False)
