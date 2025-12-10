import logging

import pandas as pd
from tkinter import messagebox

filepath = "data/users.csv"
logging.basicConfig(level = logging.INFO,
                    filename ='data/CampTrack.log',
                    filemode = 'a',
                    format='%(module)s - %(levelname)s - %(message)s')

class User:
    def __init__(self, username, password, role, status = True):
        self.username = username
        self.password = password
        self.role = role
        self.status = status

class UserManager:
    filepath = filepath

    @classmethod
    def load_users(cls):
        try:
            users = pd.read_csv(cls.filepath)
            users["password"] = users["password"].fillna("")
            return users
        except FileNotFoundError:
            users = pd.DataFrame(columns = ["username", "password", "role", "status"])
            users.to_csv(filepath, index=False)
            return users

    @classmethod
    def create_user(cls, username, password, role, treeview):
        users = cls.load_users()

        if username in users["username"].values:
            messagebox.showerror("Error", "User already exists")
            return

        if not username or not role:
            messagebox.showerror("Error", "Username or Role cannot be empty")
            return

        if role == "coordinator" and "coordinator" in users["role"].values:
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
            treeview.insert("", 'end', values = (username, password, role.title(), True))

    @classmethod
    def del_user(cls, username, treeview, frame):
        users = cls.load_users()
        users = users[users["username"] != username]
        users.to_csv(filepath, index=False)
        logging.info(f"User Deleted: {username}")
        for item in treeview.get_children():
            if treeview.item(item, "values")[0] == username:
                treeview.delete(item)
                frame.destroy()
                messagebox.showinfo("Success", f"{username} has been deleted")
                break

    @classmethod
    def edit_user(cls, username, new_username, new_password, treeview, frame):
        users = cls.load_users()

        # For debugging, so that no conflict between float64 and string
        if not new_username:
            messagebox.showerror("Error", "Username cannot be empty")
            return
        users["password"] = users["password"].astype(str)
        selected_user = (users["username"] == username)

        users.loc[selected_user, "username"] = new_username
        users.loc[selected_user, "password"] = new_password
        users.to_csv(filepath, index=False)
        logging.info(f"Changed {username} to new username {new_username} and new password {new_password}")
        frame.destroy()
        messagebox.showinfo("Success", f"Successfully Changed {username} to {new_username} and password to {new_password}")

        for item in treeview.get_children():
            if treeview.item(item, "values")[0] == username:
                treeview.item(item, values = [new_username, new_password] + list(treeview.item(item, "values")[2:]))
                break

    @classmethod
    def disable_account(cls,username):
        users = cls.load_users()
        users.loc[users["username"] == username, "status"] = False
        logging.info(f"User Disabled: {username}")
        users.to_csv(filepath, index=False)


