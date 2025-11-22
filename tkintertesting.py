import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.geometry("900x900")
root.title("Camp map")
root.resizable(False, False)

photoimagebackground_full = tk.PhotoImage(file="Group project/Algeria.png")
photoimagebackground = photoimagebackground_full.zoom(1,1)

photoimagetent_full = tk.PhotoImage(file="Group project/Tent-icon.png")
photoimagetent = photoimagetent_full.subsample(8, 8)

photoimagetent_highlighted_full = tk.PhotoImage(file="Group project/Highlighted-Tent-icon.png")
photoimagetent_highlighted = photoimagetent_highlighted_full.subsample(8, 8)              

canvas = tk.Canvas(root, width=900, height=900)
canvas.pack()
canvas_image = canvas.create_image(0, 0, anchor="nw", image=photoimagebackground)
canvas.tag_lower(canvas_image)

tent_icons = {}

positions = {
    'tent_1': (140, 450),
    'tent_2': (450, 150),
    'tent_3': (650, 250),
    'tent_4': (350, 450),
    'tent_5': (650, 450),
    'tent_6': (450, 650),
    'tent_7': (600, 700),
    'tent_8': (500, 370)
}

for tent, (x, y) in positions.items():
    
    tent_icons[canvas.create_image(x, y, anchor="c", image=photoimagetent)] = tent

canvas.img_tk = photoimagebackground
canvas.tent_normal = photoimagetent
canvas.tent_highlighted = photoimagetent_highlighted

def on_click(event, item):

    pass # add logic func here
    messagebox.showinfo(f"{tent_icons.get(item)}", f"{tent_icons.get(item)} located at ({event.x}, {event.y})")

def on_enter(item):
    
    canvas.itemconfig(item, image=canvas.tent_highlighted)

def on_leave(item):

    canvas.itemconfig(item, image=canvas.tent_normal)

def create_bind(item):

    canvas.tag_bind(item, "<Button-1>", lambda event: on_click(event, item))
    canvas.tag_bind(item, "<Enter>", lambda event: (on_enter(item)))
    canvas.tag_bind(item, "<Leave>", lambda event: (on_leave(item)))

for tent in tent_icons.keys():
    create_bind(tent)

root.mainloop()