import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
import pandas as pd
import os
from datetime import datetime
import json

# local helpers (reuse your existing functions or import them)
USERS_CSV = 'data/users.csv'
DATA_DIR = 'messages'
os.makedirs(DATA_DIR, exist_ok=True)

def conv_file(u1, u2):
    pair = sorted([str(u1), str(u2)])
    return os.path.join(DATA_DIR, f"{pair[0]}_{pair[1]}.json")

def save_message(sender, receiver, content):
    file = conv_file(sender, receiver)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {"from": sender, "to": receiver, "content": content, "timestamp": ts}
    try:
        if os.path.exists(file):
            with open(file, 'r') as f:
                data = json.load(f)
        else:
            data = []
        data.append(entry)
        with open(file, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        messagebox.showerror("Save Error", f"Could not save message data: {e}")

def load_conversation(u1, u2):
    file = conv_file(u1, u2)
    if not os.path.exists(file):
        return pd.DataFrame(columns=["from", "to", "content", "timestamp"])
    try:
        df = pd.read_json(file, dtype=str)
        if "timestamp" in df:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        return df.sort_values("timestamp")
    except Exception:
        return pd.DataFrame(columns=["from", "to", "content", "timestamp"])

def delete_conversation(u1, u2):
    file = conv_file(u1, u2)
    if os.path.exists(file):
        os.remove(file)
        return True
    return False

class MessagingApp:
    def __init__(self, root, logged_in_username):
        self.root = root
        self.logged_in_username = str(logged_in_username)
        self.users_df = self.load_users()

        # Load users and ensure logged in user exists in the list
        self.users = self.users_df.copy()
        if self.logged_in_username not in self.users['id'].astype(str).values:
            # Add user to DataFrame so it shows in lists (name==id)
            self.users = pd.concat([self.users, pd.DataFrame([{"id": self.logged_in_username, "name": self.logged_in_username}])], ignore_index=True)

        self.user_ids = list(self.users["id"])

        # current_user is fixed to logged_in_username and will be shown but disabled
        self.current_user = tk.StringVar(value=self.logged_in_username)
        self.receiver_var = tk.StringVar()

        # layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.create_widgets()

        # update receiver list initially
        self.update_receiver_options()

        
    def load_users(self):
        if os.path.exists(USERS_CSV):
            try:
                df = pd.read_csv(USERS_CSV, dtype=str, encoding='utf-8-sig')
                if 'username' in df.columns:
                    df['id'] = df['username']
                    df['name'] = df['username']
                    if 'status' in df.columns:
                        df = df[df['status'].astype(str).str.lower() == 'true']
                    return df[['id', 'name']].drop_duplicates().reset_index(drop=True)
            except Exception as e:
                messagebox.showerror("User Load Error", f"Could not read users from {USERS_CSV}: {e}. Ensure the file exists and is correctly formatted.")
        return pd.DataFrame(columns=["id", "name"])


    def create_widgets(self):
        # Frames
        self.left = tk.Frame(self.root, bg="light grey")
        self.left.grid(row=0, column = 0, padx=8, pady=8, sticky='nsew')
        self.left.grid_rowconfigure(0, weight=0)
        self.left.grid_columnconfigure(0, weight=1)

        self.right = tk.Frame(self.root, bg="light grey")
        self.right.grid(row=0, column=1, padx=8, pady=8, sticky='nsew')
        self.right.grid_rowconfigure(1, weight=1)
        self.right.grid_columnconfigure(0, weight=1)

        # Left Side
        ttk.Label(self.left, text="Current User (Sender):", font=("Comic Sans MS", 10)).grid(row=0, column=0, columnspan=2, pady=(0, 5))

        #Disable to prevent switching
        self.sender_box = ttk.Combobox(self.left,textvariable=self.current_user,values=[self.current_user.get()],state='disabled',width=20)
        self.sender_box.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        ttk.Label(self.left, text="Receiver:", font=("Comic Sans MS", 10)).grid(row=2, column=0, sticky='w')
        self.receiver_box = ttk.Combobox(self.left, textvariable=self.receiver_var, values=[], state='readonly', width=13)
        self.receiver_box.grid(row=2, column=1)

        ttk.Label(self.left, text="Message:", font=("Comic Sans MS", 10)).grid(row=3, column=0, sticky='w')
        self.msg_field = tk.Text(self.left, width=20, height=10)
        self.msg_field.grid(row=4, column=0, columnspan=2)

        ttk.Button(self.left, text="Send", command=self.send_msg).grid(row=5, column=0, columnspan=2, pady=5)


        ttk.Label(self.right, text="Conversation:", font=("Comic Sans MS", 10)).grid(row=0, column=0, pady=(0, 5), sticky='nsew')
        self.conv_panel = tk.Text(self.right, width=40, height=15, state='disabled')
        self.conv_panel.grid(row=1, column=0, sticky='nsew')

        ttk.Button(self.right, text="Load Conversation", command=self.load_conv).grid(row=2, column=0, pady=5)
        ttk.Button(self.right, text="Delete Conversation", command=self.delete_conv).grid(row=4, column=0)


    def update_receiver_options(self, *args):
        sender_id = self.current_user.get()
        receivers = [uid for uid in self.user_ids if uid != sender_id]
        self.receiver_box['values'] = receivers

        if self.receiver_var.get() == sender_id or self.receiver_var.get() not in receivers:
            self.receiver_var.set("")


        self.conv_panel.config(state='normal')
        self.conv_panel.delete("1.0", tk.END)
        self.conv_panel.insert(tk.END, f"Selected current user: {sender_id}. Select a receiver to continue.")
        self.conv_panel.config(state='disabled')

    def delete_conv(self):
        u1 = self.current_user.get()
        u2 = self.receiver_var.get()
        if not u1 or not u2:
            messagebox.showerror("Error", "Select both users")
            return
        confirm = messagebox.askyesno("Confirm Delete","Are you sure you want to delete this conversation?")
        if not confirm:
            return
        if delete_conversation(u1, u2):
            self.conv_panel.config(state='normal')
            self.conv_panel.delete("1.0", tk.END)
            self.conv_panel.insert(tk.END, "Conversation deleted.")
            self.conv_panel.config(state='disabled')
            messagebox.showinfo("Deleted", "Conversation history has been removed.")
        else:
            messagebox.showinfo("Info", "No conversation file exists to delete.")

    def send_msg(self):
        s = self.current_user.get()
        r = self.receiver_var.get()
        content = self.msg_field.get("1.0", tk.END).strip()

        if s == r:
            messagebox.showerror("Error", "Cannot send message to yourself.")
            return

        if not s or not r or not content:
            messagebox.showerror("Error", "All fields are required")
            return

        save_message(s, r, content)
        messagebox.showinfo("Sent", "Message delivered!")
        self.msg_field.delete("1.0", tk.END)
        self.load_conv()

    def load_conv(self):
        u1 = self.current_user.get()
        u2 = self.receiver_var.get()
        if not u1 or not u2:
            messagebox.showerror("Error", "Select both users")
            return

        df = load_conversation(u1, u2)
        self.conv_panel.config(state='normal')
        self.conv_panel.delete("1.0", tk.END)

        user_map = self.users.set_index('id')['name'].to_dict()

        if df.empty:
            self.conv_panel.insert(tk.END, "No messages yet.")
            self.conv_panel.config(state='disabled')
            return

        for _, row in df.iterrows():
            sender_name = user_map.get(row['from'], f"Unknown ({row['from']})")
            ts_str = row['timestamp'].strftime('%H:%M:%S') if pd.notna(row['timestamp']) else 'Unknown Time'
            line = f"[{ts_str}] {sender_name}: {row['content']}\n"
            self.conv_panel.insert(tk.END, line)

        self.conv_panel.config(state='disabled')


if __name__ == '__main__':
    os.makedirs(os.path.dirname(USERS_CSV) or '.', exist_ok=True)
    root = tk.Tk()
    #Please change this at the bottom so it changes to the login which you have made on your login_page.py tab
    MessagingApp(root, logged_in_username="admin")
    root.mainloop()
