import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import datetime
import log_coord_logic as lcl
from Msg_service import MessagingApp

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

tent_states = {'Sonelgaz Aokas': 'Available', 'Akabli': 'Available', 'Tassili n\'Ajjer': 'Available', 'Timimoun': 'Available', 'Chréa National Park': 'Available', 'Tindouf': 'Available', 'Hoggar mountains': 'Available', 'Hassi Messaoud': 'Available'}

for camp in lcl.camps.values():

    if camp.end_date + datetime.timedelta(days=1) > datetime.datetime.today() and camp.start_date < datetime.datetime.today():

        tent_states[camp.location] = 'Ongoing'

    elif camp.start_date > datetime.datetime.today() and tent_states[camp.location] != 'Ongoing':

        tent_states[camp.location] = 'Planned'

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
    msgsubframe = tk.Frame(canvas, width=500, height=280, bg="light grey", relief='solid',bd=1) # dimensions for messaging widget
    global msg_window
    msg_window = canvas.create_window(320,525, window = msgsubframe)
    #msging system here:
    MessagingApp(msgsubframe)

    global ntfsubframe
    ntfsubframe = tk.Frame(canvas, width=500, height=120, bg="white") # dimensions for notification widget
    global ntf_window
    ntf_window = canvas.create_window(320,190, window = ntfsubframe, width=500, height=120)
    #ntf system here:
    ntftitle = tk.Label(ntfsubframe, text="Notifications - Camps low on food stock:", font=("Comic Sans MS", 12), bg="white", fg="black")
    ntftitle.pack()
    lowcamps =  [camp for camp in lcl.camps.values() if camp.food_supply_per_day < camp.food_demand_per_day and camp.end_date + datetime.timedelta(days=1) >= datetime.datetime.today()]
    ntftext = ttk.Treeview(ntfsubframe, columns=("Camp Name", "Location", "Scout Leader"), show="headings")

    ntftext.heading("Camp Name", text="Camp Name")
    ntftext.heading("Location", text="Location")
    ntftext.heading("Scout Leader", text="Scout Leader")

    ntftext.column("Camp Name", width=100, anchor='center')
    ntftext.column("Location", width=100, anchor='center')
    ntftext.column("Scout Leader", width=100, anchor='center')

    for camp in lowcamps:

        ntftext.insert("",values=(camp.name, camp.location, camp.leader), index='end')

    style = ttk.Style()
    style.configure("Treeview", font=("Comic Sans MS", 10))
    style.configure("Treeview.Heading", font=("Comic Sans MS", 10, "bold"))

    ntftext.pack(expand=True, fill="both")

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

        tk.Label(mapsubframe, text=f"{tent}", font=("Comic Sans MS", 10), bg="white").place(x=x, y=y+30, anchor="n")

    #Header/ribbon:

    header = tk.Frame(canvas, borderwidth=2, bg='#1095d6')
    canvas.create_window(640, 20, window=header, width=1280, height=45)
    header.grid_columnconfigure(0, weight=1)  # left column expands to push logout to right
    header.grid_columnconfigure(1, weight=0)

    # Header contents
    tk.Label(header, text="Logistics Coordinator", font=("Comic Sans MS", 18), background='#1095d6', fg="white").grid(row=0, column=0,
                                                                                          sticky='w', padx=10,
                                                                                          pady=10)
    ttk.Button(header, text="Logout",  command = lambda: root.destroy() if messagebox.askyesno("Logout","Are you sure you want to logout?") else None).grid(row=0, column=1, sticky='e', padx=10, pady=10)


def on_click(event, item):

    if messagebox.askyesno(f"{tent_icons.get(item)}", f"{tent_states.get(tent_icons.get(item))} {tent_icons.get(item)} located at ({event.x}, {event.y}). Go to location?"):
        global current_location
        current_location = tent_icons.get(item) #maybe don't use get, just use tent_icons[item]
        loc_title = tk.Label(canvas, text=f"{current_location}", font=("Comic Sans MS", 30), fg="white", bg="#1095d6")
        loc_title.place(x=640, y=20, anchor="n")
        show_camps_treeview()
        hide_dashboard()

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

#camps_treeview_subframe:

camps_treeview_subframe = tk.Frame(canvas, width=500, height=300, bg="white")
camps_treeview_window = canvas.create_window(320,525, window = camps_treeview_subframe, width=500, height=300)

camps_listtitle = tk.Label(camps_treeview_subframe, text="Camps at this location:", font=("Comic Sans MS", 12), bg="white", fg="black")
camps_listtitle.pack()
camps_treeview = ttk.Treeview(camps_treeview_subframe, columns=("Camp Name", "Status"), show="headings")

camps_treeview.heading("Camp Name", text="Camp Name")
camps_treeview.heading("Status", text="Status")

camps_treeview.column("Camp Name", width=100, anchor='center')
camps_treeview.column("Status", width=100, anchor='center')

camps_treeview.pack(expand=True, fill="both")
canvas.itemconfigure(camps_treeview_window, state="hidden")

# Bind click on a row to a yes/no prompt
def on_camp_row_click(event):
    # Identify the row under the mouse
    row_id = camps_treeview.identify_row(event.y)
    if not row_id:
        return
    values = camps_treeview.item(row_id, "values")
    camp_name = values[0] if values else ""
    if camp_name:
        if messagebox.askyesno("Open Camp", f"Open details for '{camp_name}'?"):
            canvas.itemconfigure(create_camp_window, state="hidden")
            show_edit_camp(lcl.camps[camp_name], values[1])

camps_treeview.bind("<ButtonRelease-1>", on_camp_row_click)

def show_camps_treeview():
    canvas.itemconfigure(msg_window, state="hidden")
    canvas.itemconfigure(camps_treeview_window, state="normal")


    camps_at_location = [camp for camp in lcl.camps.values() if camp.location == current_location] # each list filled with camps (past, pres, fut) at that location.

    for camp in camps_at_location:

        if camp.end_date + datetime.timedelta(days=1) > datetime.datetime.today() and camp.start_date < datetime.datetime.today():
            camps_treeview.insert("", values=(camp.name, "ongoing"), index='end')
        elif camp.start_date > datetime.datetime.today():
            camps_treeview.insert("", values=(camp.name, "planned"), index='end')
        elif camp.end_date + datetime.timedelta(days=1) < datetime.datetime.today() :
            camps_treeview.insert("", values=(camp.name, "completed"), index='end')
#create_camp_window:

create_camp_button = tk.Button(canvas, text="Click here to create a new camp at this location", command=lambda: show_create_camp_window())
create_camp_button.config(font=("Comic Sans MS", 12), bg="lightblue", fg="black", height=2, width=40)
camp_button_window = canvas.create_window(320, 190, window=create_camp_button)
canvas.itemconfigure(camp_button_window, state="hidden")


makecampframe = tk.Frame(canvas, background="lightblue")
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
        tk.messagebox.showerror("Entry food supply error","Please enter a whole number for food supply per day")
       
    elif pay_input == "":
        tk.messagebox.showerror("Entry payment error","Please enter a number for daily payment rate")
        
    else:
        
        def date_clash(start, end, existing_camps):

            clashes = []
            for camp in existing_camps:

                if start < camp.end_date + datetime.timedelta(days=1) and end + datetime.timedelta(days=1) > camp.start_date:

                    clashes.append(True)

            return clashes

        try:
            selected_sdate = datetime.datetime(int(selected_syear), months.index(selected_smonth) + 1, int(selected_sday))
            selected_edate = datetime.datetime(int(selected_eyear), months.index(selected_emonth) + 1, int(selected_eday))

        except:

            tk.messagebox.showerror("Date error","One or more of the selected dates is non-existent")
            return

        if selected_sdate > selected_edate:
            tk.messagebox.showerror("Date error","Error! Camp end must be after start")
            
        elif selected_sdate < datetime.datetime.now() or selected_edate < datetime.datetime.now():
            tk.messagebox.showerror("Date error","Error! Camp must be set in the future")

        elif any(date_clash(selected_sdate, selected_edate, [camp for camp in lcl.camps.values() if camp.location == current_location])):
            tk.messagebox.showerror("Date clash error","Error! Camp dates clash with existing camp at this location")

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
                pay = int(pay_input)
            )

            lcl.Camp.save_camps('camps.csv')
            sdropdown_years.set("Select a start year")
            sdropdown_months.set("Select a start month")
            sdropdown_days.set("Select a start day")
            edropdown_years.set("Select an end year")
            edropdown_months.set("Select an end month")
            edropdown_days.set("Select an end day")
            camp_name_entry.delete(0, tk.END)
            food_entry.delete(0, tk.END)
            scout_payment.delete(0, tk.END)
            
            for item in camps_treeview.get_children():
                camps_treeview.delete(item)
            show_camps_treeview()

#Need to add text in the window as a user help/info, i.e. what day, overnight and exped means. Also need to do something similar for every window in app, like colour key for dashboard.

def get_years(): #check whether we can just use a list instead of function
    current_date = datetime.datetime.now()
    years = [str(current_date.year), str(current_date.year + 1)]
    return years

create_camp_label = tk.Label(Nameframe, text="Please enter camp name:", bg="lightblue", font=("Comic Sans MS", 10), fg='black')
create_camp_label.grid(column = 0, row = 0, pady=5)
camp_name_entry = tk.Entry(Nameframe, width=30, validate = "key", validatecommand = (root.register(lambda x: len(x) < 25), '%P'))
camp_name_entry.grid(column = 1, row = 0, pady=5)

create_food_label = tk.Label(Nameframe, text="Food supply per day:", bg="lightblue", font=("Comic Sans MS", 10), fg='black')
create_food_label.grid(column = 0, row = 1, pady=5)
food_entry = tk.Entry(Nameframe, width=30, validate = "key", validatecommand=(root.register(lambda x: (x.isdigit() and int(x) <100) or x == ""), '%P'))
food_entry.grid(column = 1, row = 1 , pady=5)

payment_label = tk.Label(Nameframe, text="Daily payment rate for scout leader:", bg="lightblue", font=("Comic Sans MS", 10), fg='black')
payment_label.grid(column = 0, row = 2, pady=5)
scout_payment = tk.Entry(Nameframe, width=30, validate = "key", validatecommand=(root.register(lambda x: (x.isdigit() and int(x) <10000) or x == ""), '%P'))
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

#Edit camp window:

def block_interactions(widget):

    for sequence in ("<Button>", "<ButtonRelease>", "<Motion>", "<MouseWheel>", "<Key>", "<FocusIn>", "<FocusOut>"):
        widget.bind(sequence, lambda x: "break")

    # Recurse into children
    for child in widget.winfo_children():
        block_interactions(child)

def show_edit_camp(camp, state):

    global edit_camp_window
    global root
    global editcampframe

    try:
        canvas.delete(edit_camp_window)
    except:
        pass

    editcampframe = tk.Frame(canvas, background="lightblue")
    starteditframe = tk.Frame(editcampframe, bg="lightblue")
    starteditframe.pack(side="top", padx=5, pady=5, fill="both", expand=True)
    for i in range(3):
        starteditframe.grid_columnconfigure(i, weight=1)

    endeditframe = tk.Frame(editcampframe, bg="lightblue")
    endeditframe.pack(side="top", padx=5, pady=5, fill="both", expand=True)
    for i in range(3):
        endeditframe.grid_columnconfigure(i, weight=1)

    Nameeditframe = tk.Frame(editcampframe, bg="lightblue")
    Nameeditframe.pack(side="top", padx=5, pady=5, fill="both", expand=True)

    edit_camp_label = tk.Label(Nameeditframe, text="Camp name:", bg="lightblue", font=("Comic Sans MS", 10), fg='black')
    edit_camp_label.grid(column = 0, row = 0, pady=5)
    camp_name_edit = tk.Entry(Nameeditframe, width=30, validate = "key", validatecommand = (root.register(lambda x: len(x) < 25), '%P'))
    camp_name_edit.grid(column = 1, row = 0, pady=5)
    camp_name_edit.insert(0, camp.name)

    edit_food_label = tk.Label(Nameeditframe, text="Food supply per day:", bg="lightblue", font=("Comic Sans MS", 10), fg='black')
    edit_food_label.grid(column = 0, row = 1, pady=5)
    food_edit_entry = tk.Entry(Nameeditframe, width=30, validate = "key", validatecommand=(root.register(lambda x: (x.isdigit() and int(x) <100) or x == ""), '%P'))
    food_edit_entry.grid(column = 1, row = 1 , pady=5)
    food_edit_entry.insert(0, camp.food_supply_per_day)

    demand_label = tk.Label(Nameeditframe, text="Food demand per day:", bg="lightblue", font=("Comic Sans MS", 10), fg='black')
    demand_label.grid(column = 0, row = 2, pady=5)
    demand_value_label = tk.Label(Nameeditframe, text=f"{camp.food_demand_per_day}", bg="white", font=("Comic Sans MS", 8), fg='black', width = 25, height=1, anchor="w")
    demand_value_label.grid(column = 1, row = 2, pady=5)

    #The spinbox should be linked to actual food stock data

    stock_label = tk.Label(Nameeditframe, text="Current food stock:", bg="lightblue", font=("Comic Sans MS", 10), fg='black')
    stock_label.grid(column = 0, row = 3, pady=5)
    stock_spinbox = tk.Spinbox(Nameeditframe, from_=0, to=10, increment=1, state="readonly", width=28)
    stock_spinbox.grid(column = 1, row = 3, pady=5)

    leader_label = tk.Label(Nameeditframe, text="Scout leader:", bg="lightblue", font=("Comic Sans MS", 10), fg='black')
    leader_label.grid(column = 0, row = 4, pady=5)
    leader_name_label = tk.Label(Nameeditframe, text=f"{camp.leader}", bg="white", font=("Comic Sans MS", 8), fg='black', width = 25, height=1)
    leader_name_label.grid(column = 1, row = 4, pady=5)

    edit_payment_label = tk.Label(Nameeditframe, text="Daily payment rate for scout leader:", bg="lightblue", font=("Comic Sans MS", 10), fg='black')
    edit_payment_label.grid(column = 0, row = 5, pady=5)
    scout_edit_payment = tk.Entry(Nameeditframe, width=30, validate = "key", validatecommand=(root.register(lambda x: (x.isdigit() and int(x) <10000) or x == ""), '%P'))
    scout_edit_payment.grid(column = 1, row = 5, pady=5)
    scout_edit_payment.insert(0, camp.pay)

    num_campers_label = tk.Label(Nameeditframe, text="Number of campers:", bg="lightblue", font=("Comic Sans MS", 10), fg='black')
    num_campers_label.grid(column = 0, row = 6, pady=5)
    num_campers_value_label = tk.Label(Nameeditframe, text=f"{len(camp.get_campers('campers.csv'))}", bg="white", font=("Comic Sans MS", 8), fg='black', width = 25, height=1, anchor="w")
    num_campers_value_label.grid(column = 1, row = 6, pady=5)

    #The progress bars are yet to be linked to real data

    hiking_engagement_label = tk.Label(Nameeditframe, text="Hiking engagement:", bg="lightblue", font=("Comic Sans MS", 10), fg='black')
    hiking_engagement_label.grid(column = 0, row = 7, pady=5)
    hiking_engagement_bar = ttk.Progressbar(Nameeditframe, orient="horizontal", length=185, mode="determinate")
    hiking_engagement_bar.step(50) #should be percentage of campers participating
    hiking_engagement_bar.grid(column = 1, row = 7, pady=5)

    archery_engagement_label = tk.Label(Nameeditframe, text="Archery engagement:", bg="lightblue", font=("Comic Sans MS", 10), fg='black')
    archery_engagement_label.grid(column = 0, row = 8, pady=5)
    archery_engagement_bar = ttk.Progressbar(Nameeditframe, orient="horizontal", length=185, mode="determinate")
    archery_engagement_bar.step(50) #should be percentage of campers participating
    archery_engagement_bar.grid(column = 1, row = 8, pady=5)

    rockclimbing_engagement_label = tk.Label(Nameeditframe, text="Rock climbing engagement:", bg="lightblue", font=("Comic Sans MS", 10), fg='black')
    rockclimbing_engagement_label.grid(column = 0, row = 9, pady=5)
    rockclimbing_engagement_bar = ttk.Progressbar(Nameeditframe, orient="horizontal", length=185, mode="determinate")
    rockclimbing_engagement_bar.step(50) #should be percentage of campers participating
    rockclimbing_engagement_bar.grid(column = 1, row = 9, pady=5)

    campfire_engagement_label = tk.Label(Nameeditframe, text="Campfire engagement:", bg="lightblue", font=("Comic Sans MS", 10), fg='black')
    campfire_engagement_label.grid(column = 0, row = 10, pady=5)
    campfire_engagement_bar = ttk.Progressbar(Nameeditframe, orient="horizontal", length=185, mode="determinate")
    campfire_engagement_bar.step(50) #should be percentage of campers participating
    campfire_engagement_bar.grid(column = 1, row = 10, pady=5)

    seditdropdown_years = ttk.Combobox(starteditframe, values=get_years(), state="readonly")
    seditdropdown_years.set(f"{camp.start_date.year}")
    seditdropdown_years.grid(row=0, column=0, padx=10, pady=5, sticky="ew")


    seditdropdown_months = ttk.Combobox(starteditframe, values=months, state="readonly")
    seditdropdown_months.set(f"{months[camp.start_date.month -1]}")
    seditdropdown_months.grid(row=0, column=1, padx=10, pady=5, sticky="ew")


    seditdropdown_days = ttk.Combobox(starteditframe, values=days, state="readonly")
    seditdropdown_days.set(f"{camp.start_date.day}")
    seditdropdown_days.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

    eeditdropdown_years = ttk.Combobox(endeditframe, values=get_years(), state="readonly")
    eeditdropdown_years.set(f"{camp.end_date.year}")
    eeditdropdown_years.grid(row=0, column=0, padx=10, pady=5, sticky="ew")


    eeditdropdown_months = ttk.Combobox(endeditframe, values=months, state="readonly")
    eeditdropdown_months.set(f"{months[camp.end_date.month -1]}")
    eeditdropdown_months.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    eeditdropdown_days = ttk.Combobox(endeditframe, values=days, state="readonly")
    eeditdropdown_days.set(f"{camp.end_date.day}")
    eeditdropdown_days.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

    def edit_button_select():

        selected_syear = seditdropdown_years.get()
        selected_smonth = seditdropdown_months.get()
        selected_sday = seditdropdown_days.get()
        selected_eyear = eeditdropdown_years.get()
        selected_emonth = eeditdropdown_months.get()
        selected_eday = eeditdropdown_days.get()
        camp_name_input = camp_name_edit.get().strip()
        food_input = food_edit_entry.get()
        pay_input = scout_edit_payment.get()
        
        if camp_name_input == "":
            tk.messagebox.showerror("Entry camp name error","Please enter a name for the camp")

        elif camp_name_input in lcl.camps and camp_name_input != camp.name:
            tk.messagebox.showerror("Entry camp name error","Camp name already exists, please enter a different name")
            
        elif food_input == "":
            tk.messagebox.showerror("Entry food supply error","Please enter a whole number for food supply per day")
        
        elif pay_input == "":
            tk.messagebox.showerror("Entry payment error","Please enter a number for daily payment rate")
            
        else:
            
            def date_clash(start, end, existing_camps):

                clashes = []
                for c in existing_camps:

                    if c.name != camp.name and start < c.end_date + datetime.timedelta(days=1) and end + datetime.timedelta(days=1) > c.start_date:

                        clashes.append(True)

                return clashes

            try:
                selected_sdate = datetime.datetime(int(selected_syear), months.index(selected_smonth) + 1, int(selected_sday))
                selected_edate = datetime.datetime(int(selected_eyear), months.index(selected_emonth) + 1, int(selected_eday))

            except:

                tk.messagebox.showerror("Date error","One or more of the selected dates is non-existent")
                return

            if selected_sdate > selected_edate:
                tk.messagebox.showerror("Date error","Error! Camp end must be after start")
                
            elif state != 'ongoing' and (selected_sdate < datetime.datetime.now() or selected_edate < datetime.datetime.now()):
                tk.messagebox.showerror("Date error","Error! Camp must be set in the future")

            elif any(date_clash(selected_sdate, selected_edate, [c for c in lcl.camps.values() if c.location == current_location])):
                tk.messagebox.showerror("Date clash error","Error! Camp dates clash with existing camp at this location")

            else:
                tk.messagebox.showinfo("Edit success", f"You have successfully edited this camp: {camp_name_input} on the selected dates: {selected_sdate.strftime('%Y-%m-%d')} to {selected_edate.strftime('%Y-%m-%d')} with food stock of {food_input} per day and daily payment rate of {pay_input} دج ")
                
                if selected_sdate == selected_edate:

                    camp_type = 'day'

                elif (selected_edate - selected_sdate).days == 1:

                    camp_type = 'overnight'

                else:

                    camp_type = 'expedition'
                
                camp.name = camp_name_input
                camp.start_date = selected_sdate
                camp.end_date = selected_edate
                camp.food_supply_per_day = int(food_input)
                camp.pay = int(pay_input)
                camp.camp_type = camp_type

                lcl.Camp.save_camps('camps.csv')

    edit_camp_button = tk.Button(Nameeditframe, text="Save changes", command=edit_button_select)
    edit_camp_button.grid(row=11, column=1, pady=5)

    edit_camp_window = canvas.create_window(960, 400, window=editcampframe, width=500, height=500)
    canvas.itemconfigure(edit_camp_window, state="normal")

    if state == "completed":

        block_interactions(editcampframe)
        editcampframe.configure(cursor="X_cursor")

    elif state == "ongoing":

        block_interactions(starteditframe)
        block_interactions(endeditframe)
        block_interactions(food_edit_entry)
        starteditframe.configure(cursor="X_cursor")
        endeditframe.configure(cursor="X_cursor")
        food_edit_entry.configure(cursor="X_cursor")


def hide_dashboard():

    canvas.itemconfigure(create_camp_window, state="normal")
    canvas.itemconfigure(map_window, state="hidden")
    canvas.itemconfigure(ntf_window, state="hidden")
    canvas.itemconfigure(msg_window, state="hidden")
    canvas.itemconfigure(camp_button_window, state = "normal")

def show_create_camp_window():

    try:
        canvas.delete(edit_camp_window)

    except:
        pass

    finally:
        canvas.itemconfigure(create_camp_window, state="normal")


#root.protocol("WM_DELETE_WINDOW", lambda: None)
root.mainloop()
