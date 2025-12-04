import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import datetime
from ScoutLeader import ScoutLeader

root = tk.Tk()
root.geometry("1280x720")
root.resizable(False, False)
root.title("CampTrack / Name of the role here / Dashboard") #Maybe this should be username instead?

canvas = tk.Canvas(root, width="1280", height="720", bg="white")
canvas.pack(expand=True, fill="both")

bg = tk.PhotoImage(file="Desert.png")
canvas_bg = canvas.create_image(0, 0, image=bg, anchor="nw")
canvas.tag_lower(canvas_bg)

# Ensures only a given leader's camps will be shown, when logging in can simply set username as some variable but for now have to assign manually
placeholder = "leader1"
leaders = ScoutLeader.load_leaders("data/users.csv")
selected_leader = leaders[placeholder]
camp_dict = selected_leader.load_camps_for_leader("data/camps.csv")

welcome = canvas.create_text(
    -600, 360,
    text = f"Welcome, {selected_leader.username}!",
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

    algeria_map = tk.PhotoImage(file="map.png")


algeria_map = tk.PhotoImage(file="map.png")

photoimagetent = tk.PhotoImage(file="Tent-icon.png")

photoimagetent_highlighted = tk.PhotoImage(file="Highlighted-Tent-icon.png")

photoimageavailable = tk.PhotoImage(file="green.png")

photoimageavailable_highlighted = tk.PhotoImage(file="Highlighted-green.png")

photoimageplanned = tk.PhotoImage(file="amber.png")

photoimageplanned_highlighted = tk.PhotoImage(file="Highlighted-amber.png")

tent_icons = {}

location_coords = {'Sonelgaz Aokas': (310, 40), 'Akabli': (190, 330), 'Tassili n\'Ajjer': (365, 270), 'Timimoun': (210, 220), 'Chréa National Park': (220, 100), 'Tindouf': (50, 245), 'Hoggar mountains': (333, 389), 'Hassi Messaoud': (340, 170)}

# creates a dictionary of camps for only the selected leader
#def create_leader_dict(dict):
 #   leader_camps = {}
  #  for key, value in dict.items():
   #     if value.location in location_coords:
    #        leader_camps[value.location] = location_coords[value.location]
    #return leader_camps


def show_others(): #maybe also add a key above the map for tent icons

    global mapsubframe
    mapsubframe = tk.Frame(canvas, bg="lightblue", width=500, height=500) #dimensions for right plank window
    global map_window
    map_window = canvas.create_window(960, 400, window=mapsubframe)
    #A window here
    global mapsubcanvas
    mapsubcanvas = tk.Canvas(mapsubframe, width='500', height='500', bg='white')

    mapsubcanvas.tent = photoimagetent
    mapsubcanvas.tent_highlighted = photoimagetent_highlighted

    mapsubcanvas.pack()
    mapsubcanvas.create_image(250, 250, image=algeria_map)



    positions = leaders[placeholder].create_leader_dict(camp_dict, location_coords)
    print(positions)













    #mapsubframe_canvas = tk.Canvas(mapsubframe, width=500, height=500, bg="white", highlightthickness=0)
    #mapsubframe_canvas.pack(expand=True, fill="both")

    #mapsubframe.map_bg = tk.PhotoImage(file="map.png")
    #mapsubframe_canvas.create_image(0, 0, image=mapsubframe.map_bg, anchor="nw")


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

    # How comes this function was called before it was defined in Mahesh's and Sairam's code??

    def on_click(event, item):
        if messagebox.askyesno(f"{tent_icons.get(item)}",
                               f"{tent_icons.get(item)} located at ({event.x}, {event.y}). Go to location?"):
            global current_location
            current_location = tent_icons.get(item)  # maybe don't use get, just use tent_icons[item]
            loc_title = tk.Label(canvas, text=f"{current_location}", font=("Comic Sans MS", 30), fg="white",
                                 bg="#1095d6")
            loc_title.place(x=640, y=20, anchor="n")
            show_camps_listbox()
            show_create_camp_window()


    def on_enter(item):

        mapsubcanvas.itemconfig(item, image=mapsubcanvas.tent_highlighted)

    def on_leave(item):

        mapsubcanvas.itemconfig(item, image=mapsubcanvas.tent)

    # code needed to be modified here for some reason to work properly
    def create_bind(item):
        mapsubcanvas.tag_bind(item, "<Button-1>", lambda event: on_click(event, item))
        mapsubcanvas.tag_bind(item, "<Enter>", lambda event: (on_enter(item)))
        mapsubcanvas.tag_bind(item, "<Leave>", lambda event: (on_leave(item)))

    camps_listbox_subframe = tk.Frame(canvas, width=500, height=300, bg="lightblue")
    camps_listbox_window = canvas.create_window(320, 525, window=camps_listbox_subframe, width=500, height=300)
    camps_listbox = tk.Listbox(camps_listbox_subframe)

    def show_camps_listbox():
        canvas.itemconfigure(msg_window, state="hidden")
        canvas.itemconfigure(camps_listbox_window, state="normal")

    makecampframe = tk.Frame(canvas, background="lightblue")
    makecampframe.pack(padx=0, pady=0, fill="both", expand=True)

    # msging system here
    # rewriting this as a function to delay to allow code to work

    for tent, (x,y) in positions.items():
        item = mapsubcanvas.create_image(x, y, anchor="c", image=photoimagetent)
        tent_icons[item] = tent
        create_bind(item)

    #Header/ribbon:

    header = tk.Frame(canvas, borderwidth=2, bg='#1095d6')
    canvas.create_window(640, 20, window=header, width=1280, height=45)
    header.grid_columnconfigure(0, weight=1)  # left column expands to push logout to right
    header.grid_columnconfigure(1, weight=0)

    # Header contents
    tk.Label(header, text=placeholder, font=("Comic Sans MS", 18), background='#1095d6', fg="white").grid(row=0, column=0,
                                                                                          sticky='w', padx=10,
                                                                                          pady=10)
    ttk.Button(header, text="Logout").grid(row=0, column=1, sticky='e', padx=10, pady=10) #add command 'logout' to this

    create_camp_window = canvas.create_window(960, 400, window=makecampframe, width=500, height=500)
    canvas.itemconfigure(create_camp_window, state="hidden")

    def show_create_camp_window():
        canvas.itemconfigure(create_camp_window, state="normal")
        canvas.itemconfigure(map_window, state="hidden")

root.mainloop()
