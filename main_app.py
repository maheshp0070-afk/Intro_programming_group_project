import tkinter as tk
from admin_GUI import AdminPage
from login_page import LoginPage
from admin_logic import *
import pandas as pdg

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

        #Initialises Frames
        for F in (LoginPage, AdminPage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(LoginPage)

    def show_frame(self, page_ident):
        self.frames[page_ident].tkraise()

root = App()
root.geometry("1280x720")
root.resizable(False, False)
root.mainloop()