import tkinter as tk
from tkinter import ttk
from admin_logic import create_user

class AdminPage(tk.Frame):
    def __init__(self, App, controller):
        super().__init__(App)
        self.controller = controller
        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight = 1)

        # Making Header
        header = tk.Frame(self, borderwidth=2, relief="ridge", bg = 'lightgrey')
        header.grid(sticky='ew')
        header.columnconfigure(0, weight=1) # left column expands to push logout to right

        # Header contents
        tk.Label(header, text="Admin Dashboard", font=("Arial", 18)).grid(row=0, column=0, sticky='w', padx=10, pady=10)
        ttk.Button(header, text="Logout", command=self.logout).grid(row=0, column=1, sticky='e', padx=10, pady=10)

        # --- Main Content Frame ---
        # Creating Body Frame
        body = tk.Frame(self, bg = 'grey')
        body.grid(sticky = 'nsew')
        body.grid_rowconfigure(0, weight = 1)
        body.grid_columnconfigure(1, weight = 1)

        def callback():
            pass

        sidebar = ttk.Treeview(body)
        sidebar.grid(sticky = 'ns')
        sidebar.heading("#0", text="User Management")
        sidebar.insert('', 0, 'item1', text = 'Add User')
        sidebar.bind('<<TreeviewSelect>>', callback)
        sidebar.config(selectmode = 'browse')

        content = tk.Frame(body, bg='white')
        content.grid(row=0, column=1, sticky='nsew')
        ttk.Button(content, text="Add User", command= lambda: create_user(new_username.get(), new_password.get(), " ")).grid()

        new_username = ttk.Entry(content)
        new_password = ttk.Entry(content)
        new_username.grid()
        new_password.grid()

    def logout(self):
        from login_page import loginpage
        self.controller.show_frame(loginpage)

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Admin Page Test")
    page = AdminPage(root, root)
    page.pack(fill = 'both', expand = True)
    root.state('zoomed')
    root.mainloop()
