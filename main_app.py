import tkinter as tk
from tkinter import ttk, messagebox
import logging
from admin_GUI import AdminPage
from login_page import loginpage
from admin_logic import *

logging.basicConfig(level = logging.DEBUG,
                    filename = 'CampTrack.log',
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

        for F in (loginpage, AdminPage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column =0,  sticky='nsew')

        self.show_frame(loginpage)


    def show_frame(self, page_ident):
        self.frames[page_ident].tkraise()



root = App()
root.mainloop()