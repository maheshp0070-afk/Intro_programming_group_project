import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import datetime
import log_coord_logic as lcl

lcl.Admin.load_users('users.csv')
lcl.Coordinator.load_users('users.csv')
lcl.Leader.load_users('users.csv')
lcl.User.load_all_users('users.csv')
lcl.Camp.load_camps('camps.csv')

for user in lcl.all_users.values():

    if user.role == 'coordinator':

        coordinator = user
        break

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
    text = f"Welcome, {coordinator.username}!",
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

photoimagetent = tk.PhotoImage(file="Tent-icon.png")

photoimagetent_highlighted = tk.PhotoImage(file="Highlighted-Tent-icon.png")

photoimageavailable = tk.PhotoImage(file="green.png")

photoimageavailable_highlighted = tk.PhotoImage(file="Highlighted-green.png")

photoimageplanned = tk.PhotoImage(file="amber.png")

photoimageplanned_highlighted = tk.PhotoImage(file="Highlighted-amber.png")

tent_icons = {}

positions = {'Sonelgaz Aokas': (310, 40), 'Akabli': (190, 330), 'Tassili n\'Ajjer': (365, 270), 'Timimoun': (210, 220), 'Chréa National Park': (220, 100), 'Tindouf': (50, 245), 'Hoggar mountains': (333, 389), 'Hassi Messaoud': (340, 170)}

tent_states = {'Sonelgaz Aokas': 'Ongoing', 'Akabli': 'Ongoing', 'Tassili n\'Ajjer': 'Ongoing', 'Timimoun': 'Planned', 'Chréa National Park': 'Available', 'Tindouf': 'Available', 'Hoggar mountains': 'Available', 'Hassi Messaoud': 'Available'}

def show_others(): #maybe also add a key above the map for tent icons

    global mapsubframe
    mapsubframe = tk.Frame(canvas, bg="lightblue", width=500, height=500) #dimensions for right plank window
    global map_window
    map_window = canvas.create_window(960, 400, window=mapsubframe)

    global mapsubcanvas
    mapsubcanvas = tk.Canvas(mapsubframe, width='500', height='500', bg = 'white')

    mapsubcanvas.tent_normal = photoimagetent
    mapsubcanvas.tent_highlighted = photoimagetent_highlighted
    mapsubcanvas.available = photoimageavailable
    mapsubcanvas.available_highlighted = photoimageavailable_highlighted
    mapsubcanvas.planned = photoimageplanned
    mapsubcanvas.planned_highlighted = photoimageplanned_highlighted

    mapsubcanvas.pack()
    mapsubcanvas.create_image(250, 250, image=algeria_map)

    global msgsubframe
    msgsubframe = tk.Frame(canvas, width=500, height=300, bg="white") # dimensions for messaging widget
    global msg_window
    msg_window = canvas.create_window(320,525, window = msgsubframe)
    #msging system here

    global ntfsubframe
    ntfsubframe = tk.Frame(canvas, width=500, height=120, bg="white") # dimensions for notification widget
    global ntf_window
    ntf_window = canvas.create_window(320,190, window = ntfsubframe)
    #see below how we implemented map to other subframe to implement further

    for tent, (x, y) in positions.items():

        if tent_states[tent] == 'Ongoing':

            item = mapsubcanvas.create_image(x, y, anchor="c", image=photoimagetent)
            tent_icons[item] = tent
            create_bind(item)

        elif tent_states[tent] == 'Available':

            item = mapsubcanvas.create_image(x, y, anchor="c", image=photoimageavailable)
            tent_icons[item] = tent
            create_bind(item)

        elif tent_states[tent] == 'Planned':

            item = mapsubcanvas.create_image(x, y, anchor="c", image=photoimageplanned)
            tent_icons[item] = tent
            create_bind(item)

    #Header/ribbon:

    header = tk.Frame(canvas, borderwidth=2, bg='#1095d6')
    canvas.create_window(640, 20, window=header, width=1280, height=45)
    header.grid_columnconfigure(0, weight=1)  # left column expands to push logout to right
    header.grid_columnconfigure(1, weight=0)

    # Header contents
    tk.Label(header, text="Logistics Coordinator", font=("Comic Sans MS", 18), background='#1095d6', fg="white").grid(row=0, column=0,
                                                                                          sticky='w', padx=10,
                                                                                          pady=10)
    ttk.Button(header, text="Logout").grid(row=0, column=1, sticky='e', padx=10, pady=10) #add command 'logout' to this


def on_click(event, item):

    if messagebox.askyesno(f"{tent_icons.get(item)}", f"{tent_states.get(tent_icons.get(item))} {tent_icons.get(item)} located at ({event.x}, {event.y}). Go to location?"):
        global current_location
        current_location = tent_icons.get(item) #maybe don't use get, just use tent_icons[item]
        loc_title = tk.Label(canvas, text=f"{current_location}", font=("Comic Sans MS", 30), fg="white", bg="#1095d6")
        loc_title.place(x=640, y=20, anchor="n")
        show_camps_listbox()
        show_create_camp_window()

def on_enter(item):

    if tent_states.get(tent_icons.get(item)) == 'Ongoing':

        mapsubcanvas.itemconfig(item, image=mapsubcanvas.tent_highlighted)

    elif tent_states.get(tent_icons.get(item)) == 'Available':

        mapsubcanvas.itemconfig(item, image=mapsubcanvas.available_highlighted)

    elif tent_states.get(tent_icons.get(item)) == 'Planned':

        mapsubcanvas.itemconfig(item, image=mapsubcanvas.planned_highlighted)

def on_leave(item):

    if tent_states.get(tent_icons.get(item)) == 'Ongoing':

        mapsubcanvas.itemconfig(item, image=mapsubcanvas.tent_normal)

    elif tent_states.get(tent_icons.get(item)) == 'Available':

        mapsubcanvas.itemconfig(item, image=mapsubcanvas.available)

    elif tent_states.get(tent_icons.get(item)) == 'Planned':

        mapsubcanvas.itemconfig(item, image=mapsubcanvas.planned)

def create_bind(item):
    mapsubcanvas.tag_bind(item, "<Button-1>", lambda event: on_click(event, item))
    mapsubcanvas.tag_bind(item, "<Enter>", lambda event: (on_enter(item)))
    mapsubcanvas.tag_bind(item, "<Leave>", lambda event: (on_leave(item)))

#camps_listbox_subframe:

camps_listbox_subframe = tk.Frame(canvas, width=500, height=300, bg="lightblue")
camps_listbox_window = canvas.create_window(320,525, window = camps_listbox_subframe, width=500, height=300)
camps_listbox = tk.Listbox(camps_listbox_subframe)

#camps_at_locations = {'tent_1': [], 'tent_2': [], 'tent_3': [], 'tent_4': [], 'tent_5': [], 'tent_6': [], 'tent_7': [], 'tent_8': []} # each list to be filled with camps (past, pres, fut) at that location.

tent_1_camps = ['camp1', 'camp2', 'camp3']

for camp in tent_1_camps:
    camps_listbox.insert(tk.END, camp)

camps_listbox.pack(expand=True, fill="both")
canvas.itemconfigure(camps_listbox_window, state="hidden")

def show_camps_listbox():
    canvas.itemconfigure(msg_window, state="hidden")
    canvas.itemconfigure(camps_listbox_window, state="normal")

#create_camp_window:

makecampframe = tk.Frame(canvas, background="lightblue")
makecampframe.pack(padx=0, pady=0, fill="both", expand=True)
startframe = tk.Frame(makecampframe, bg="lightblue")
startframe.pack(side="top", padx=5, pady=10, fill="both", expand=True)
for i in range(3):
    startframe.grid_columnconfigure(i, weight=1)

endframe = tk.Frame(makecampframe, bg="lightblue")
endframe.pack(side="top", padx=5, pady=10, fill="both", expand=True)
for i in range(3):
    endframe.grid_columnconfigure(i, weight=1)

Nameframe = tk.Frame(makecampframe, bg="lightblue")
Nameframe.pack(side="top", padx=5, pady=10, fill="both", expand=True)

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
days = [str(i) for i in range(1, 32)]

def button_select():
    selected_syear = sdropdown_years.get()
    selected_smonth = sdropdown_months.get()
    selected_sday = sdropdown_days.get()
    selected_eyear = edropdown_years.get()
    selected_emonth = edropdown_months.get()
    selected_eday = edropdown_days.get()
    camp_name_input = camp_name_entry.get().strip()
    food_input = food_entry.get()
    pay_input = scout_payment.get()
    if (selected_syear == "Select a start year" or selected_smonth == "Select a start month" or selected_sday == "Select a start day" or selected_eyear == "Select an end year" or selected_emonth == "Select an end month" or selected_eday == "Select an end day"):
        tk.messagebox.showerror("Entry date error","Please enter dates in all the dropdown boxes")
       
    elif camp_name_input == "":
        tk.messagebox.showerror("Entry camp name error","Please enter a name for the camp")

    elif camp_name_input in lcl.camps:
        tk.messagebox.showerror("Entry camp name error","Camp name already exists, please enter a different name")
        
    elif food_input == "":
        tk.messagebox.showerror("Entry food stock error","Please enter a whole number for food stock per day")
       
    elif pay_input == "":
        tk.messagebox.showerror("Entry payment error","Please enter a number for daily payment rate")
        
    else:

        try:
            selected_sdate = datetime.datetime(int(selected_syear), months.index(selected_smonth) + 1, int(selected_sday))
            selected_edate = datetime.datetime(int(selected_eyear), months.index(selected_emonth) + 1, int(selected_eday))

        except:

            tk.messagebox.showerror("Date error","One or more of the selected dates is non-existent")
            return

        if selected_sdate > selected_edate:
            tk.messagebox.showerror("Date error","Error!, camp end must be after start")
            
        elif selected_sdate < datetime.datetime.now() or selected_edate < datetime.datetime.now():
            tk.messagebox.showerror("Date error","Error!, camp must be set in the future")
            
        else:
            tk.messagebox.showinfo("Creation success", f"You have successfully created camp: {camp_name_input} on the selected dates: {selected_sdate.strftime('%Y-%m-%d')} to {selected_edate.strftime('%Y-%m-%d')} with food stock of {food_input} per day and daily payment rate of {pay_input} دج ") #location to be added, e.g. akfadou. Also to be formatted diff if day/overnight/expedition
            
            if selected_sdate == selected_edate:

                camp_type = 'day'

            elif (selected_edate - selected_sdate).days == 1:

                camp_type = 'overnight'

            else:

                camp_type = 'expedition'
            
            coordinator.create_camp(
                camps_dict = lcl.camps,
                name = camp_name_input,
                location = current_location,
                camp_type = camp_type,
                start_date = selected_sdate,
                end_date = selected_edate,
                food_supply_per_day = int(food_input),
                pay = float(pay_input)
            )

            lcl.Camp.save_camps('camps.csv')

#Need to add text in the window as a user help/info, i.e. what day, overnight and exped means. Also need to do something similar for every window in app, like colour key for dashboard.

def get_years(): #check whether we can just use a list instead of function
    current_date = datetime.datetime.now()
    years = [str(current_date.year), str(current_date.year + 1)]
    return years

create_camp_label = tk.Label(Nameframe, text="Please enter camp name:", bg="lightblue", font=("Comic Sans MS", 10), fg='black')
create_camp_label.grid(column = 0, row = 0, pady=5)
camp_name_entry = tk.Entry(Nameframe, width=30, validate = "key", validatecommand = (root.register(lambda x: len(x) < 25), '%P'))
camp_name_entry.grid(column = 1, row = 0, pady=5)

create_food_label = tk.Label(Nameframe, text="Food stock available per day:", bg="lightblue", font=("Comic Sans MS", 10), fg='black')
create_food_label.grid(column = 0, row = 1, pady=5)
food_entry = tk.Entry(Nameframe, width=30, validate = "key", validatecommand=(root.register(lambda x: (x.isdigit() and int(x) <99 ) or x == ""), '%P'))
food_entry.grid(column = 1, row = 1 , pady=5)

payment_label = tk.Label(Nameframe, text="Daily payment rate for scout leader:", bg="lightblue", font=("Comic Sans MS", 10), fg='black')
payment_label.grid(column = 0, row = 2, pady=5)
scout_payment = tk.Entry(Nameframe, width=30, validate = "key", validatecommand=(root.register(lambda x: (x.isdigit() and int(x) <999) or x == ""), '%P'))
scout_payment.grid(column = 1, row = 2 , pady=5)

sdropdown_years = ttk.Combobox(startframe, values=get_years(), state="readonly")
sdropdown_years.set("Select a start year")
sdropdown_years.grid(row=0, column=0, padx=10, pady=10, sticky="ew")


sdropdown_months = ttk.Combobox(startframe, values=months, state="readonly")
sdropdown_months.set("Select a start month")
sdropdown_months.grid(row=0, column=1, padx=10, pady=10, sticky="ew")


sdropdown_days = ttk.Combobox(startframe, values=days, state="readonly")
sdropdown_days.set("Select a start day")
sdropdown_days.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

edropdown_years = ttk.Combobox(endframe, values=get_years(), state="readonly")
edropdown_years.set("Select an end year")
edropdown_years.grid(row=0, column=0, padx=10, pady=10, sticky="ew")


edropdown_months = ttk.Combobox(endframe, values=months, state="readonly")
edropdown_months.set("Select an end month")
edropdown_months.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

edropdown_days = ttk.Combobox(endframe, values=days, state="readonly")
edropdown_days.set("Select an end day")
edropdown_days.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

date_button = tk.Button(Nameframe, text="Create camp", command=button_select)
date_button.grid(row=3, column=1, pady=20)

create_camp_window = canvas.create_window(960, 400, window=makecampframe, width=500, height=500)
canvas.itemconfigure(create_camp_window, state="hidden")


def show_create_camp_window():

    canvas.itemconfigure(create_camp_window, state="normal")
    canvas.itemconfigure(map_window, state="hidden")

root.mainloop()
