"""
Import Modules
"""
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import datetime
from ScoutLeader import ScoutLeader




"""
Core Setup (Root/Canvas Creation + Leader and Camp Data Loading)
"""
# Root/Canvas Creation
root = tk.Tk()
root.geometry("1280x720")
root.resizable(False, False)
root.title("CampTrack / Name of the role here / Dashboard") #Maybe this should be username instead?

canvas = tk.Canvas(root, width="1280", height="720", bg="white")
canvas.pack(expand=True, fill="both")

bg = tk.PhotoImage(file="Desert.png")
canvas_bg = canvas.create_image(0, 0, image=bg, anchor="nw")
canvas.tag_lower(canvas_bg)

# Loads leader and corresponding camp data
placeholder = "leader1"
leaders = ScoutLeader.load_leaders("data/users.csv")
selected_leader = leaders[placeholder]
camp_dict = selected_leader.load_camps_for_leader("data/camps.csv")




"""
Welcome Animation and Boards slide-down
"""
welcome = canvas.create_text(
    -600, 360,
    text = f"Welcome, {selected_leader.username}!",
    font = ("Comic Sans MS", 40, "bold"),
    fill = "forest green"
)

# Welcome animation sliding functions
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

# Creating memory for Map and Notification Board slide-down widgets
map_board = tk.PhotoImage(file="map_board.png")
canvas_map_board = canvas.create_image(960, -400, image=map_board)

notif_msg_board = tk.PhotoImage(file="notif_msg_boards.png")
canvas_map_notif_msg_board = canvas.create_image(320, -400, image=notif_msg_board)

# Slide-down function for Map and Notification Board widgets
def show_widgets():

    x, y = canvas.coords(canvas_map_board)

    if y < 360:

        canvas.move(canvas_map_board, 0, 45)
        canvas.move(canvas_map_notif_msg_board, 0, 45)
        canvas.after(15, show_widgets)

    else:

        canvas.after(300, show_others)




"""
Saving Globally-used images and variables in memory
"""
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




"""
Show the frames of the main GUI after the welcome animation and board slide-downs are complete
"""
def show_others(): #maybe also add a key above the map for tent icons
    """
    MAP FRAME: Placing a frame on the Map Board, then placing the map canvas inside the frame 
    (which contains the map and tent icons)
    """
    
    """ MAP FRAME (& Canvas) creation"""
    global mapsubframe
    mapsubframe = tk.Frame(canvas, bg="lightblue", width=500, height=500) #dimensions for right plank window
    global map_window
    map_window = canvas.create_window(960, 400, window=mapsubframe)
    global mapsubcanvas
    mapsubcanvas = tk.Canvas(mapsubframe, width='500', height='500', bg='white')

    mapsubcanvas.pack()
    mapsubcanvas.create_image(250, 250, image=algeria_map)
    # Storing tent images in canvas memory for access in event functions
    mapsubcanvas.tent = photoimagetent
    mapsubcanvas.tent_highlighted = photoimagetent_highlighted

    """LOGIC for tent icon interactions on the map canvas & subsequent window/frames"""
    # Click event function for tent icons
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

    # Hover event functions for tent icons
    def on_enter(item):

        mapsubcanvas.itemconfig(item, image=mapsubcanvas.tent_highlighted)

    def on_leave(item):

        mapsubcanvas.itemconfig(item, image=mapsubcanvas.tent)

    # Binding function for tent icons
    def create_bind(item):
        mapsubcanvas.tag_bind(item, "<Button-1>", lambda event: on_click(event, item))
        mapsubcanvas.tag_bind(item, "<Enter>", lambda event: (on_enter(item)))
        mapsubcanvas.tag_bind(item, "<Leave>", lambda event: (on_leave(item)))

    """ CAMP LISTBOX FRAME: Placing a frame on the Message Board, then placing the camp listbox inside the frame """
    camps_listbox_subframe = tk.Frame(canvas, width=500, height=300, bg="lightblue")
    camps_listbox_window = canvas.create_window(320, 525, window=camps_listbox_subframe, width=500, height=300)
    camps_listbox = tk.Listbox(camps_listbox_subframe)
    canvas.itemconfigure(camps_listbox_window, state="hidden")

    def show_camps_listbox():
        canvas.itemconfigure(msg_window, state="hidden")
        canvas.itemconfigure(camps_listbox_window, state="normal")

    positions = leaders[placeholder].create_leader_dict(camp_dict, location_coords)
    print(positions)

    """ CAMP CREATION FRAME AND WINDOW: triggers upon clicking and entering a tent icon """
    createcampframe = tk.Frame(canvas, background="lightblue")
    create_camp_window = canvas.create_window(960, 400, window=createcampframe, width=500, height=500)
    canvas.itemconfigure(create_camp_window, state="hidden")

    def show_create_camp_window():
        canvas.itemconfigure(create_camp_window, state="normal")
        canvas.itemconfigure(map_window, state="hidden")


    #mapsubframe_canvas = tk.Canvas(mapsubframe, width=500, height=500, bg="white", highlightthickness=0)
    #mapsubframe_canvas.pack(expand=True, fill="both")

    #mapsubframe.map_bg = tk.PhotoImage(file="map.png")
    #mapsubframe_canvas.create_image(0, 0, image=mapsubframe.map_bg, anchor="nw")


    """
    MESSAGE FRAME: Placing a frame on the Message Board, then placing the messaging app inside the frame
    """
    global msgsubframe
    msgsubframe = tk.Frame(canvas, width=500, height=300, bg="white") # dimensions for messaging widget
    global msg_window
    msg_window = canvas.create_window(320,525, window = msgsubframe)
    # Instantiate the MessagingApp from Msg_service (same call as in admin_GUI.py)
    # Import locally to avoid top-level import issues — same pattern as AdminPage.
    try:
        from Msg_service import MessagingApp
        print("msgsubframe:", msgsubframe, "type:", type(msgsubframe))
        print("msg_window:", msg_window, "type:", type(msg_window))
        MessagingApp(msgsubframe)
    except Exception as e:
        # If MessagingApp import/initialisation fails we show a placeholder and print the error
        tk.Label(msgsubframe, text="Messaging unavailable", font=("Comic Sans MS", 14)).pack(padx=10, pady=10)
        print("Failed to load MessagingApp:", e)
    # --- End messaging widget ---


    """
    BACK TO MAP FRAME: Placing a frame on the Message Board, then placing 2 button widgets 
    inside the frame (one for TBC, one for going back to the map)
    """
    """Logic for "Back to Dashboard" Button"""
    def show_main_dashboard():
        # Make sure the main map and messaging windows are visible
        canvas.itemconfigure(map_window, state="normal")
        canvas.itemconfigure(msg_window, state="normal")
        # Hide the other overlay windows
        canvas.itemconfigure(create_camp_window, state="hidden")
        canvas.itemconfigure(camps_listbox_window, state="hidden")
        # Ensure they are above other items (raise them)
        try:
            canvas.tag_raise(map_window)
            canvas.tag_raise(msg_window)
        except Exception:
            print("Error raising map or message window to top layer")
        # Geometry realignment of widgets
        root.update_idletasks()
    
    """Button Frame/window + Button Creation"""
    global ntfsubframe
    ntfsubframe = tk.Frame(canvas, width=500, height=120, bg="lightblue") # dimensions for notification widget
    ntfsubframe.grid_columnconfigure(0, weight=1)
    ntfsubframe.grid_columnconfigure(1, weight=1)
    ttk.Button(ntfsubframe, text="Back to Dashboard",
           command=show_main_dashboard).grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    ttk.Button(ntfsubframe, text="Coming Soon").grid(row=0, column=1, padx=10, pady=10, sticky="ew")
    global ntf_window
    ntf_window = canvas.create_window(320,190, window = ntfsubframe)






    for tent, (x,y) in positions.items():
        item = mapsubcanvas.create_image(x, y, anchor="c", image=photoimagetent)
        tent_icons[item] = tent
        create_bind(item)

    """
    HEADER/RIBBON creation: Creating a header/ribbon frame at the top of the GUI
    """
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

    







"""
EXECUTE THE GUI!!!
"""  
root.mainloop()
