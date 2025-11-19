import logging, csv
from tkinter import *
import pandas as pd
from tkinter import messagebox

class User():
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

def create_user(username, password, role):
    try:
        with open("users_database.csv", "r") as file:
            users = pd.read_csv(file)
    except FileNotFoundError:
        users = pd.DataFrame(columns = ["Username", "Password", "Role", "is_active"])
        users.to_csv("users_database.csv", index=False)

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
        new_user.to_csv("users_database.csv", mode = 'a', index=False, header = False)
        logging.info(f"New User Created: {username}")
        messagebox.showinfo("Success", "New User has been added")

def del_user(username):
        users = pd.read_csv("users_database.csv")
        users = users[users["Username"] != username]
        users.to_csv("users_database.csv", index=False)

def edit_user(username, new_username, new_password):
    users = pd.read_csv("users_database.csv")
    selected_user = users["Username"] == username
    users.loc[selected_user, "Username"] = new_username
    users.loc[selected_user, "Password"] = new_password
    users.to_csv("users_database.csv", index=False)

def disable_account(username):
    users = pd.read_csv("users_database.csv")
    users.loc[users["Username"] == username, "is_active"] = False
