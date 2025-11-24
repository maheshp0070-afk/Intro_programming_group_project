import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.geometry("1280x720")
root.resizable(False, False)
root.title("CampTrack / Logistics Coordinator / Dashboard") #Maybe this should be username instead?

canvas = tk.Canvas(root, width="1280", height="720", bg="white")
canvas.pack(expand=True, fill="both")

bg = tk.PhotoImage(file="background.png")
canvas_bg = canvas.create_image(0, 0, image=bg, anchor="nw")
canvas.tag_lower(canvas_bg)

welcome = canvas.create_text(
    -600, 360,
    text = "Welcome, Logistics Coordinator!", #Don't make this username as it could be too long..
    font = ("Tsukushi A Round Gothic", 75, "bold"),
    fill = "white"
)

def slide_in():

    x, y = canvas.coords(welcome)

    if x < 640:

        canvas.move(welcome, 15, 0)
        canvas.after(15, slide_in)

    else:

        canvas.after(2000, slide_out)

def slide_out():

    x, y = canvas.coords(welcome)

    if x < 1880:

        canvas.move(welcome, 15, 0)
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

        canvas.move(canvas_map_board, 0, 15)
        canvas.move(canvas_map_notif_msg_board, 0, 15)
        canvas.after(15, show_widgets)

    else:

        canvas.after(300, show_others)

algeria_map = tk.PhotoImage(file="map.png")

photoimagetent_full = tk.PhotoImage(file="Tent-icon.png")
photoimagetent = photoimagetent_full.subsample(8, 8)

photoimagetent_highlighted_full = tk.PhotoImage(file="Highlighted-Tent-icon.png")
photoimagetent_highlighted = photoimagetent_highlighted_full.subsample(8, 8)

tent_icons = {}

positions = {
    'tent_1': (788, 400),
    'tent_2': (960, 233),
    'tent_3': (1071, 289),
    'tent_4': (904, 400),
    'tent_5': (1071, 400),
    'tent_6': (960, 511),
    'tent_7': (1043, 539),
    'tent_8': (988, 356)
}

canvas.tent_normal = photoimagetent
canvas.tent_highlighted = photoimagetent_highlighted

def show_others():

    canvas.create_image(960, 400, image=algeria_map)

    for tent, (x, y) in positions.items():

        item = canvas.create_image(x, y, anchor="c", image=photoimagetent)

        tent_icons[item] = tent

        create_bind(item)

def on_click(event, item):
    pass  # add logic func here
    messagebox.showinfo(f"{tent_icons.get(item)}", f"{tent_icons.get(item)} located at ({event.x}, {event.y})")

def on_enter(item):
    canvas.itemconfig(item, image=canvas.tent_highlighted)

def on_leave(item):
    canvas.itemconfig(item, image=canvas.tent_normal)

def create_bind(item):
    canvas.tag_bind(item, "<Button-1>", lambda event: on_click(event, item))
    canvas.tag_bind(item, "<Enter>", lambda event: (on_enter(item)))
    canvas.tag_bind(item, "<Leave>", lambda event: (on_leave(item)))

root.mainloop()