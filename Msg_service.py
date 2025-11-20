import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import os
from datetime import datetime

USERS_CSV = 'users.csv'  
DATA_DIR = 'messages'
os.makedirs(DATA_DIR, exist_ok=True)

def load_users():
    if os.path.exists(USERS_CSV):
        return pd.read_csv(USERS_CSV, dtype=str)
    else:
        df = pd.DataFrame([
            ["A", "Alice"],
            ["B", "Bob"],
            ["C", "Charlie"],
            ["D", "Diana"]
        ], columns=["id", "name"])
        df.to_csv(USERS_CSV, index=False)
        return df

users_df = load_users()

def conv_file(u1, u2):
    pair = sorted([str(u1), str(u2)])
    return os.path.join(DATA_DIR, f"{pair[0]}_{pair[1]}.json")

def save_message(sender, receiver, content):
    file = conv_file(sender, receiver)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = {
        "from": sender,
        "to": receiver,
        "content": content,
        "timestamp": ts
    }

    if os.path.exists(file):
        df = pd.read_json(file, dtype=str)
    else:
        df = pd.DataFrame(columns=["from", "to", "content", "timestamp"])

    df.loc[len(df)] = entry
    df.to_json(file, orient="records", indent=4)

def load_conversation(u1, u2):
    file = conv_file(u1, u2)
    if not os.path.exists(file):
        return pd.DataFrame(columns=["from", "to", "content", "timestamp"])

    df = pd.read_json(file, dtype=str)
    if "timestamp" in df:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df.sort_values("timestamp")

def delete_conversation(u1, u2):
    file = conv_file(u1, u2)
    if os.path.exists(file):
        os.remove(file)
        return True
    return False

class MessagingApp:
    def __init__(self, root):
        self.root = root
        root.title("Messaging Service")

        self.users = users_df

        # Frames
        self.left = ttk.Frame(root)
        self.left.grid(row=0, column=0, padx=10, pady=10)

        self.right = ttk.Frame(root)
        self.right.grid(row=0, column=1, padx=10, pady=10)

        # Sender
        ttk.Label(self.left, text="Sender:").grid(row=0, column=0)
        self.sender_var = tk.StringVar()
        self.sender_box = ttk.Combobox(self.left, textvariable=self.sender_var,values=list(self.users["id"]))
        self.sender_box.grid(row=0, column=1)

        # Receiver
        ttk.Label(self.left, text="Receiver:").grid(row=1, column=0)
        self.receiver_var = tk.StringVar()
        self.receiver_box = ttk.Combobox(self.left, textvariable=self.receiver_var,values=list(self.users["id"]))
        self.receiver_box.grid(row=1, column=1)

        # Message
        ttk.Label(self.left, text="Message:").grid(row=2, column=0)
        self.msg_field = tk.Text(self.left, width=30, height=5)
        self.msg_field.grid(row=2, column=1)

        #Delete Button
        ttk.Button(self.right, text="Delete Conversation", command=self.delete_conv).grid(row=3, column=0, pady=5)

        # Send button
        ttk.Button(self.left, text="Send", command=self.send_msg).grid(row=3, column=1, pady=5)

        # Conversation panel
        ttk.Label(self.right, text="Conversation:").grid(row=0, column=0)
        self.conv_panel = tk.Text(self.right, width=60, height=25)
        self.conv_panel.grid(row=1, column=0)

        ttk.Button(self.right, text="Load Conversation", command=self.load_conv).grid(row=2, column=0, pady=5)

    def delete_conv(self):
        u1 = self.sender_var.get()
        u2 = self.receiver_var.get()

        if not u1 or not u2:
            messagebox.showerror("Error", "Select both users")
            return

        confirm = messagebox.askyesno("Confirm Delete",
                                  "Are you sure you want to delete this conversation?")
        if not confirm:
            return

        if delete_conversation(u1, u2):
            self.conv_panel.delete("1.0", tk.END)
            self.conv_panel.insert(tk.END, "Conversation deleted.")
            messagebox.showinfo("Deleted", "Conversation history has been removed.")
        else:
            messagebox.showinfo("Info", "No conversation file exists to delete.")

    def send_msg(self):
        s = self.sender_var.get()
        r = self.receiver_var.get()
        content = self.msg_field.get("1.0", tk.END).strip()

        if not s or not r or not content:
            messagebox.showerror("Error", "All fields are required")
            return

        save_message(s, r, content)
        messagebox.showinfo("Sent", "Message delivered!")
        self.msg_field.delete("1.0", tk.END)

    def load_conv(self):
        u1 = self.sender_var.get()
        u2 = self.receiver_var.get()

        if not u1 or not u2:
            messagebox.showerror("Error", "Select both users")
            return

        df = load_conversation(u1, u2)
        self.conv_panel.delete("1.0", tk.END)

        if df.empty:
            self.conv_panel.insert(tk.END, "No messages yet.")
            return

        for _, row in df.iterrows():
            sender_match = self.users[self.users['id'] == row['from']]
            sender_name = sender_match['name'].values[0] if not sender_match.empty else f"Unknown ({row['from']})"

            line = f"[{row['timestamp']}] {sender_name}: {row['content']}\n"
            self.conv_panel.insert(tk.END, line)

if __name__ == '__main__':
    root = tk.Tk()
    MessagingApp(root)
    root.mainloop()
