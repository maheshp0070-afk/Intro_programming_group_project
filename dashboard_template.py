import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import datetime

root = tk.Tk()
root.geometry("1280x720")
root.resizable(False, False)
root.title("CampTrack / Name of the role here / Dashboard") #Maybe this should be username instead?

canvas = tk.Canvas(root, width="1280", height="720", bg="white")
canvas.pack(expand=True, fill="both")

bg = tk.PhotoImage(file="Desert.png")
canvas_bg = canvas.create_image(0, 0, image=bg, anchor="nw")
canvas.tag_lower(canvas_bg)

welcome = canvas.create_text(
    -600, 360,
    text = f"Welcome, ...!",
    font = ("Comic Sans MS", 40, "bold"),
    fill = "forest green"
)

def slide_in():

    x, y = canvas.coords(welcome)

    if x < 640:

        canvas.move(welcome, 45, 0)
        canvas.after(15, slide_in)

    else:

        canvas.after(2000, slide_out)

def slide_out():

    x, y = canvas.coords(welcome)

    if x < 1880:

        canvas.move(welcome, 45, 0)
        canvas.after(15, slide_out)

    else:

        canvas.itemconfig(welcome, text = "")
        canvas.after(300, show_widgets)

slide_in()

map_board = tk.PhotoImage(file="map_board.png")
canvas_map_board = canvas.create_image(960, -400, image=map_board)

notif_msg_board = tk.PhotoImage(file="notif_msg_boards.png")
canvas_map_notif_msg_board = canvas.create_image(320, -400, image=notif_msg_board)

def show_widgets():

    x, y = canvas.coords(canvas_map_board)

    if y < 360:

        canvas.move(canvas_map_board, 0, 45)
        canvas.move(canvas_map_notif_msg_board, 0, 45)
        canvas.after(15, show_widgets)

    else:

        canvas.after(300, show_others)

def show_others(): #maybe also add a key above the map for tent icons

    global mapsubframe
    mapsubframe = tk.Frame(canvas, bg="lightblue", width=500, height=500) #dimensions for right plank window
    global map_window
    map_window = canvas.create_window(960, 400, window=mapsubframe)
    #A window here

    global msgsubframe
    msgsubframe = tk.Frame(canvas, width=500, height=300, bg="white") # dimensions for messaging widget
    global msg_window
    msg_window = canvas.create_window(320,525, window = msgsubframe)
    #msging system here

    global ntfsubframe
    ntfsubframe = tk.Frame(canvas, width=500, height=120, bg="white") # dimensions for notification widget
    global ntf_window
    ntf_window = canvas.create_window(320,190, window = ntfsubframe)
    #notficiations or anything else you want here

    #Header/ribbon:

    header = tk.Frame(canvas, borderwidth=2, bg='#1095d6')
    canvas.create_window(640, 20, window=header, width=1280, height=45)
    header.grid_columnconfigure(0, weight=1)  # left column expands to push logout to right
    header.grid_columnconfigure(1, weight=0)

    # Header contents
    tk.Label(header, text="Name of the role here", font=("Comic Sans MS", 18), background='#1095d6', fg="white").grid(row=0, column=0,
                                                                                          sticky='w', padx=10,
                                                                                          pady=10)
    ttk.Button(header, text="Logout").grid(row=0, column=1, sticky='e', padx=10, pady=10) #add command 'logout' to this

root.mainloop()
