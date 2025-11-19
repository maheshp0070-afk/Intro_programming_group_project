import tkinter as tk
from tkinter import messagebox

class GUI:
    
    def __init__(self):
        
        self.root = tk.Tk()

        self.menubar = tk.Menu(self.root)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        
        self.filemenu.add_command(label='Close', command=exit)
        self.menubar.add_cascade(menu=self.filemenu, label='Exit')
        
        self.campers_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(menu=self.campers_menu, label='Campers')
        
        self.camps_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(menu=self.camps_menu, label='Camps')

        self.usercreation = tk.Menu(self.campers_menu, tearoff=0)
        self.userdeletion = tk.Menu(self.campers_menu, tearoff=0)
        self.campers_menu.add_cascade(menu=self.usercreation, label='Create User')
        self.campers_menu.add_cascade(menu=self.usercreation, label='Delete User')
        #Add more here I kinda forgot all of the functions

        self.campcreation = tk.Menu(self.camps_menu, tearoff=0)
        self.campdeletion = tk.Menu(self.camps_menu, tearoff=0)
        self.camps_menu.add_cascade(menu=self.campcreation, label='Create Camp')
        self.camps_menu.add_cascade(menu=self.campdeletion, label='Delete camp')

        self.root.config(menu=self.menubar)
        
        self.label = tk.Label(self.root, text='Your Message Here', font=('Arial', 18))
        self.label.pack(padx=10, pady=10)

        self.textbox = tk.Text(self.root, height=4, font=('Arial', 16))
        self.textbox.pack(padx=10, pady=10)

        self.check_state = tk.IntVar()

        self.check = tk.Checkbutton(self.root, text='Show my Message', font=('Arial', 16), variable=self.check_state)
        self.check.pack(padx=10, pady=10)

        self.button = tk.Button(self.root, text='Submit', font=('Arial', 16), command=self.show_message)
        self.button.pack(padx=10, pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def show_message(self):
        if self.check_state.get() == 0:
            print(self.textbox.get('1.0', tk.END))
        else:
            messagebox.showinfo(title='Message', message=self.textbox.get('1.0', tk.END))

    def on_closing(self):
        if messagebox.askyesno(title= 'Quit?', message='Do you want to leave?'):
            self.root.destroy()
        else:
            pass

GUI()
