import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.geometry("1280x720")
root.resizable(False, False)
root.title("CampTrack / Logistics Coordinator / Dashboard") #Maybe this should be username instead?

canvas = tk.Canvas(root, width="1280", height="720", bg="white")
canvas.pack(expand=True, fill="both")

bg = tk.PhotoImage(file="Desert.png")
canvas_bg = canvas.create_image(0, 0, image=bg, anchor="nw")
canvas.tag_lower(canvas_bg)

welcome = canvas.create_text(
    -600, 360,
    text = "Welcome, Logistics Coordinator!", #Don't make this username as it could be too long..
    font = ("Comic Sans MS", 40, "bold"),
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

positions = {'tent_1': (78, 250), 'tent_2': (250, 83), 'tent_3': (361, 139), 'tent_4': (194, 250), 'tent_5': (361, 250), 'tent_6': (250, 361), 'tent_7': (333, 389), 'tent_8': (278, 206)}









def show_others():

    global mapsubframe
    mapsubframe = tk.Frame(canvas, bg="lightblue", width=500, height=500) #dimensions for right plank window
    canvas.create_window(960, 400, window=mapsubframe)

    global mapsubcanvas
    mapsubcanvas = tk.Canvas(mapsubframe, width='500', height='500', bg = 'white')

    mapsubcanvas.tent_normal = photoimagetent
    mapsubcanvas.tent_highlighted = photoimagetent_highlighted

    mapsubcanvas.pack()
    mapsubcanvas.create_image(250, 250, image=algeria_map)


    global msgsubframe
    msgsubframe = tk.Frame(canvas, width=500, height=300, bg="white") # dimentions for messaging widget
    canvas.create_window(320,525, window = msgsubframe)
    #msging system here

    global ntfsubframe
    ntfsubframe = tk.Frame(canvas, width=500, height=120, bg="white") # dimensions for notification widget
    canvas.create_window(320,190, window = ntfsubframe)
    #see below how we implemented map to other subframe to implement further




    for tent, (x, y) in positions.items():

        item = mapsubcanvas.create_image(x, y, anchor="c", image=photoimagetent)

        tent_icons[item] = tent

        create_bind(item)

def on_click(event, item):
    pass  # add logic func here
    messagebox.showinfo(f"{tent_icons.get(item)}", f"{tent_icons.get(item)} located at ({event.x}, {event.y})")

def on_enter(item):
    mapsubcanvas.itemconfig(item, image=mapsubcanvas.tent_highlighted)

def on_leave(item):
    mapsubcanvas.itemconfig(item, image=mapsubcanvas.tent_normal)

def create_bind(item):
    mapsubcanvas.tag_bind(item, "<Button-1>", lambda event: on_click(event, item))
    mapsubcanvas.tag_bind(item, "<Enter>", lambda event: (on_enter(item)))
    mapsubcanvas.tag_bind(item, "<Leave>", lambda event: (on_leave(item)))

root.mainloop()
