import logging, csv
from tkinter import *
import pandas as pd
from tkinter import messagebox

filepath = "data/users_database.csv"

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
            users = pd.DataFrame(columns = ["Username", "Password", "Role", "is_active"])
            users.to_csv(filepath, index=False)


    @classmethod
    def create_user(cls, username, password, role):
        users = cls.load_users()
        users_list = users["Username"].tolist()
        print(users_list)
        if username in users["Username"].values:
            messagebox.showerror("Error", "User already exists")
            return

        if "Logistics Coordinator" in users["Role"].values:
            messagebox.showerror("Error", "Only One Logistics Coordinator Allowed")
            return

        else:
            new_user = pd.DataFrame([{
                "Username" : username,
                "Password" : password,
                "Role" : role,
                "is_active" : True}])
            new_user.to_csv(filepath, mode = 'a', index=False, header = False)
            logging.info(f"New User Created: {username}")
            messagebox.showinfo("Success", "New User has been added")

    @classmethod
    def del_user(cls, username):
        users = cls.load_users()
        users = users[users["Username"] != username]
        users.to_csv(filepath, index=False)
        logging.info(f"User Deleted: {username}")

    @classmethod
    def edit_user(cls, username, new_username, new_password):
        users = cls.load_users()
        selected_user = (users["Username"] == username)
        users.loc[selected_user, "Username"] = new_username
        users.loc[selected_user, "Password"] = new_password
        users.to_csv(filepath, index=False)
        logging.info(f"Changed {username} to new username {new_username} and new password {new_password}")

    @classmethod
    def disable_account(cls,username):
        users = cls.load_users()
        users.loc[users["Username"] == username, "is_active"] = False
        logging.info(f"User Disabled: {username}")
        users.to_csv(filepath, index=False)
