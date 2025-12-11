import logging

import pandas as pd
from tkinter import messagebox

filepath = "data/users.csv"
logging.basicConfig(level = logging.INFO,
                    filename ='data/CampTrack.log',
                    filemode = 'a',
                    format='%(module)s - %(levelname)s - %(message)s')
camps = pd.read_csv("data/camps.csv")

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
    def create_user(cls, username, password, role, treeview, messageframe):
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
            for widget in messageframe.winfo_children():
                widget.destroy()
            from msg_system import MessagingApp
            MessagingApp(messageframe, logged_in_username="admin")

    @classmethod
    def del_user(cls, username, treeview, frame, messageframe):
        users = cls.load_users()
        if username in camps["leader"].astype(str).values:
            messagebox.showerror("Error", "Actively Assigned Users Cannot Be Deleted")
            return
        users = users[users["username"] != username]
        users.to_csv(filepath, index=False)
        logging.info(f"User Deleted: {username}")
        for widget in messageframe.winfo_children():
            widget.destroy()
        from msg_system import MessagingApp
        MessagingApp(messageframe, logged_in_username="admin")

        for item in treeview.get_children():
            if treeview.item(item, "values")[0] == username:
                treeview.delete(item)
                messagebox.showinfo("Success", f"{username} has been deleted")
                break

    @classmethod
    def edit_user(cls, username, new_username, new_password, treeview, frame, messageframe):
        users = cls.load_users()

        # For debugging, so that no conflict between float64 and string
        if not new_username:
            messagebox.showerror("Error", "Username cannot be empty")
            return

        if new_username in users["username"].values:
            messagebox.showerror("Error", "User Already Exists")
            return

        users["password"] = users["password"].astype(str)
        selected_user = (users["username"] == username)
        users.loc[selected_user, "username"] = new_username
        users.loc[selected_user, "password"] = new_password
        users.to_csv(filepath, index=False)

        camps["leader"] = camps["leader"].replace(username, new_username)
        camps.to_csv("data/camps.csv", index=False)
        logging.info(f"Changed {username} to New Username {new_username} And New Password {new_password}")
        messagebox.showinfo("Success", f"Successfully Changed {username} To {new_username} And Password To {new_password}")

        for widget in messageframe.winfo_children():
            widget.destroy()
        from msg_system import MessagingApp
        MessagingApp(messageframe, logged_in_username="admin")

        for item in treeview.get_children():
            if treeview.item(item, "values")[0] == str(username):
                treeview.item(item, values = [new_username, new_password] + list(treeview.item(item, "values")[2:]))
                break

    @classmethod
    def enable_user(cls, username, frame, treeview):
        users = cls.load_users()
        users.loc[users["username"] == username, "status"] = True
        users.to_csv(filepath, index=False)
        logging.info(f"User {username} Enabled")

        messagebox.showinfo("Success", f"Successfully Enabled {username}")
        for item in treeview.get_children():
            if treeview.item(item, "values")[0] == username:
                old_values = list(treeview.item(item, "values"))
                old_values[3] = "True"
                treeview.item(item, values=old_values)
                break

    @classmethod
    def disable_user(cls, username, frame, treeview):
        users = cls.load_users()
        if username in camps["leader"].astype(str).values:
            messagebox.showerror("Error", "Actively Assigned Users Cannot Be Disabled")
            return

        users.loc[users["username"] == username, "status"] = False
        users.to_csv(filepath, index=False)
        messagebox.showinfo("Success", f"Successfully Disabled {username}")
        logging.info(f"User {username} Disabled")

        for item in treeview.get_children():
            if treeview.item(item, "values")[0] == username:
                old_values = list(treeview.item(item, "values"))
                old_values[3] = "False"
                treeview.item(item, values=old_values)
                break




