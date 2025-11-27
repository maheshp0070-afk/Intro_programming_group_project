import tkinter as tk
from tkinter import ttk
from admin_logic import *

class AdminPage(tk.Frame):
    def __init__(self, App, controller):
        super().__init__(App)
        self.controller = controller

        # Creates Canvas for GUI
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(expand=True, fill="both")

        # Adds Background Photo
        self.bg = tk.PhotoImage(file="background.png")
        self.canvas_bg = self.canvas.create_image(0, 0, image=self.bg, anchor="nw")
        self.canvas.tag_lower(self.canvas_bg)

        welcome = self.canvas.create_text(
            -600, 360,
            text="Welcome, Admin!",
            font=("Comic Sans MS", 40, "bold"),
            fill="white"
        )

        def slide_in():

            x, y = self.canvas.coords(welcome)

            if x < 640:

                self.canvas.move(welcome, 30, 0)
                self.canvas.after(30, slide_in)

            else:

                self.canvas.after(2000, slide_out)

        def slide_out():

            x, y = self.canvas.coords(welcome)

            if x < 1880:

                self.canvas.move(welcome, 15, 0)
                self.canvas.after(15, slide_out)

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

                self.canvas.move(self.canvas_map_board, 0, 15)
                self.canvas.move(self.canvas_map_notif_msg_board, 0, 15)
                self.canvas.after(15, show_widgets)

            else:

                self.canvas.after(300, show_others)


        def show_others():

            self.userslist_subframe = tk.Frame(self.canvas, bg="lightblue", width=500, height=500)  # dimensions for right plank window
            self.canvas.create_window(960, 400, window=self.userslist_subframe)

            self.msgsubframe = tk.Frame(self.canvas, width=500, height=280, bg="white")  # dimensions for messaging widget
            self.canvas.create_window(320, 525, window=self.msgsubframe)
            # msging system here


            self.adduser_subframe = tk.Frame(self.canvas, width=500, height=140, bg="white")  # dimensions for notification widget
            self.canvas.create_window(320, 190, window=self.adduser_subframe)
            new_username = ttk.Entry(self.adduser_subframe, font=("Comic Sans MS", 20, "bold"))
            new_password = ttk.Entry(self.adduser_subframe, font=("Comic Sans MS", 20, "bold"))
            new_username.pack()
            new_password.pack()
        # Making Header
        #header = tk.Frame(self, borderwidth=2, relief="ridge", bg = 'lightgrey')
        #header.grid(sticky='ew')
        #header.columnconfigure(0, weight=1) # left column expands to push logout to right

        # Header contents
        #tk.Label(header, text="Admin Dashboard", font=("Arial", 18)).grid(row=0, column=0, sticky='w', padx=10, pady=10)
        #ttk.Button(header, text="Logout", command=self.logout).grid(row=0, column=1, sticky='e', padx=10, pady=10)



        def callback():
            pass


        #ttk.Button(self, text="Add User", command= lambda: UserManager.create_user(new_username.get(), new_password.get(), " ")).grid()



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
