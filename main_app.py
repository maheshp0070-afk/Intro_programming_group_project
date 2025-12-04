import tkinter as tk
from admin_GUI import AdminPage
from login_page import LoginPage
from admin_logic import *
import pandas as pd

logging.basicConfig(level = logging.DEBUG,
                    filename ='data/CampTrack.log',
                    filemode = 'a',
                    format='%(module)s - %(levelname)s - %(message)s')

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CampTrack")
        self.state('zoomed')
        self.container = tk.Frame(self)
        self.container.grid()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.frames = {}

        #Loads Users
        self.users = self.init_users()

        #Initialises Frames
        for F in (LoginPage, AdminPage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(LoginPage)

    @classmethod
    def init_users(cls):
        users_list = {}
        df = UserManager.load_users()
        for _, row in df.iterrows():
            users_list[row["Username"]] = User(row["Username"], row["Password"], row["Role"], row["is_active"])
        return users_list

    def show_frame(self, page_ident):
        self.frames[page_ident].tkraise()

root = App()
root.mainloop()