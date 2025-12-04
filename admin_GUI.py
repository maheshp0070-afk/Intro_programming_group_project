import tkinter as tk
from tkinter import ttk
from admin_logic import *
import subprocess
import threading

class AdminPage(tk.Frame):
    def __init__(self, App, controller):
        super().__init__(App)
        self.controller = controller

        def play_startup_sound():
            self.sound_file = "sans..wav"
            subprocess.call(["afplay", self.sound_file])

        # Creates Canvas for GUI
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(expand=True, fill="both")

        # Adds Background Photo
        self.bg = tk.PhotoImage(file="Desert.png")
        self.canvas_bg = self.canvas.create_image(0, 0, image=self.bg, anchor="nw")
        self.canvas.tag_lower(self.canvas_bg)

        welcome = self.canvas.create_text(
            -600, 360,
            text=f"Welcome, Admin!",
            font=("Comic Sans MS", 40, "bold"),
            fill="forest green"
        )

        def slide_in():

            x, y = self.canvas.coords(welcome)

            if x < 640:

                self.canvas.move(welcome, 45, 0)
                self.canvas.after(45, slide_in)

            else:

                self.canvas.after(2000, slide_out)

        def slide_out():

            x, y = self.canvas.coords(welcome)

            if x < 1880:

                self.canvas.move(welcome, 45, 0)
                self.canvas.after(45, slide_out)

            else:

                self.canvas.itemconfig(welcome, text="")
                self.canvas.after(300, show_widgets)

        slide_in()

        #Creates the different boards
        self.map_board = tk.PhotoImage(file="map_board.png")
        self.canvas_map_board = self.canvas.create_image(960, -400, image=self.map_board)

        self.notif_msg_board = tk.PhotoImage(file="notif_msg_boards.png")
        self.canvas_map_notif_msg_board = self.canvas.create_image(320, -400, image=self.notif_msg_board)

        def show_widgets():

            x, y = self.canvas.coords(self.canvas_map_board)

            if y < 360:
                self.canvas.move(self.canvas_map_board, 0, 45)
                self.canvas.move(self.canvas_map_notif_msg_board, 0, 45)
                self.canvas.after(15, show_widgets)

            else:
                self.canvas.after(300, show_others)

        def show_others():
            # Making Header
            header = tk.Frame(self.canvas, borderwidth=2, bg='#1095d6')
            self.canvas.create_window(640, 20, window=header, width=1280, height=45)
            header.grid_columnconfigure(0, weight=1)  # left column expands to push logout to right
            header.grid_columnconfigure(1, weight=0)

            # Header contents
            tk.Label(header, text="Admin Dashboard", font=("Comic Sans MS", 18), background='#1095d6', fg = "white").grid(row=0, column=0,
                                                                                                  sticky='w', padx=10,
                                                                                                  pady=10)
            tk.Button(header, text="Logout", command=self.logout, bg="#1095d6", bd=0, relief = "flat").grid(row=0, column=1, sticky='e', padx=10, pady=10)

            # Create GUI for users list
            self.userslist_subframe = tk.Frame(self.canvas, bg="white", width=500,
                                               height=500, relief = 'solid', bd=1)  # dimensions for right plank window
            self.canvas.create_window(960, 420, window=self.userslist_subframe)

            tk.Label(self.userslist_subframe, text= "Users List", font=("Comic Sans MS", 20, "bold"), bg="white").pack()
            display_columns = ["Username", "Password", "Role", "Active?"]
            users = UserManager.load_users()
            users["role"] = users["role"].str.title()
            users_treeview = ttk.Treeview(self.userslist_subframe, selectmode="browse", columns = display_columns, show = "headings", height = 14)
            style = ttk.Style()
            style.configure("Treeview", font=("Comic Sans MS", 15, "bold"), rowheight=30)
            style.configure("Treeview.Heading", font=("Comic Sans MS", 20, "bold"), rowheight = 60)
            users_treeview.pack(side="left", fill="both", expand=True)

            for col in display_columns:
                users_treeview.heading(col, text=col)
                users_treeview.column(col, width = 160, anchor = "center")
            for index, row in users.iterrows():
                users_treeview.insert("", index, values = list(row.fillna("")))

            users_treeview.column("Active?", width=100)

            # Add Scrollbar
            yscroll = ttk.Scrollbar(self.userslist_subframe, orient = "vertical", command = users_treeview.yview)
            yscroll.pack(side="right", fill="y")
            users_treeview.config(yscrollcommand=yscroll.set)

            def on_select(event):
                self.edituserframe = tk.Frame(self.userslist_subframe, bg="white", bd=2, relief="raised")
                self.edituserframe.place(relx=0.5, rely=0.5, anchor="center", width=595, height=500)
                tk.Button(self.edituserframe, text="Exit",command = close).place(relx=1, rely=0, anchor="ne")
                tr

            users_treeview.bind('<<TreeviewSelect>>', on_select)

            def close():
                self.edituserframe.destroy()

           #Creates GUI For Messaging System
            self.msgsubframe = tk.Frame(self.canvas, width=500, height=280, bg ="light grey", relief = 'solid', bd=1)  # dimensions for messaging widget
            self.canvas.create_window(320, 525, window=self.msgsubframe)
            from Msg_service import MessagingApp
            MessagingApp(self.msgsubframe)

            self.adduser_subframe = tk.Frame(self.canvas, width=500, height=140, bg="#b3794a", relief = 'solid', bd=1)  # dimensions for notification widget
            self.canvas.create_window(320, 190, window=self.adduser_subframe)

            # GUI for Creating User
            tk.Label(self.adduser_subframe, text="New Username:", font=("Comic Sans MS", 15), bg="#b3794a", fg="white").grid(row=0, column=0)
            tk.Label(self.adduser_subframe, text="New Password:", font=("Comic Sans MS", 15), bg="#b3794a", fg="white").grid(row=1, column=0)
            tk.Label(self.adduser_subframe, text="Select Role:", font = ("Comic Sans MS", 15), bg="#b3794a", fg="white").grid(row=2, column=0)
            new_username = tk.Entry(self.adduser_subframe, font=("Comic Sans MS", 15, "bold"), width = 35, validate="key", validatecommand = (self.register(lambda x: len(x)<20), '%P'))
            new_password = tk.Entry(self.adduser_subframe, font=("Comic Sans MS", 15, "bold"), width = 35,)
            new_username.grid(row=0, column = 1, padx=5)
            new_password.grid(row=1, column = 1, padx=5)
            user_role = ttk.Combobox(self.adduser_subframe)
            user_role.grid(row=2, column=1, padx=5, sticky = 'w')
            user_role.config(values = ("Coordinator", "Scout Leader"), width = 34, font=("Comic Sans MS", 15, "bold"), state="readonly")
            tk.Button(self.adduser_subframe, text="Create User", bg = '#b3794a', font = ("Comic Sans MS", 18, "bold"),
                       command=lambda: UserManager.create_user(new_username.get(), new_password.get(), user_role.get(), users_treeview)).grid(row=3, columnspan=2)

            #threading.Thread(target=play_startup_sound, daemon=True).start()

    def logout(self):
        from login_page import LoginPage
        self.controller.show_frame(LoginPage)

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Admin Page Test")
    root.geometry("1280x720")
    page = AdminPage(root, root)
    page.pack(fill = 'both', expand = True)
    root.mainloop()
