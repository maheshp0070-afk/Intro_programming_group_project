"""
Import Modules
"""
import csv
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import datetime
from types import SimpleNamespace
from ScoutLeader import ScoutLeader
import pandas as pd




"""
Core Setup (Root Window / Canvas Creation + Background Image on canvas)
"""
# Defines which leader the code will be showing
placeholder = "leader2"
# Root/Canvas Creation
root = tk.Tk()
root.geometry("1280x720")
root.resizable(False, False)
root.title(f"CampTrack / {placeholder} / Dashboard")

canvas = tk.Canvas(root, width="1280", height="720", bg="white")
canvas.pack(expand=True, fill="both")

bg = tk.PhotoImage(file="Desert.png")
canvas_bg = canvas.create_image(0, 0, image=bg, anchor="nw")
canvas.tag_lower(canvas_bg)




"""
Leader and Camp Data Loading
"""
CAMPS_FILE = "data/camps.csv"
leaders = ScoutLeader.load_leaders("data/users.csv")
selected_leader = leaders[placeholder]
camp_dict = selected_leader.load_camps_for_leader(CAMPS_FILE)




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

location_coords = {
    "Sonelgaz Aokas": (310, 40),
    "Akabli": (190, 330),
    "Tassili n'Ajjer": (365, 270),
    "Timimoun": (210, 220),
    "Chréa National Park": (220, 100),
    "Tindouf": (50, 245),
    "Hoggar mountains": (333, 389),
    "Hassi Messaoud": (340, 170),
}




"""
GLOBAL FUNCTIONS FOR CAMPS
"""
"""Release completed camps by clearing their leader after end date + 1 day grace period."""
def release_completed_camps():
    now = datetime.datetime.now()
    updated_rows = []
    changed = False

    try:
        with open(CAMPS_FILE, newline="", encoding="utf-8") as csvfile:
            # DictReader to read each CSV row into a dictionary where keys are column headers
            reader = csv.DictReader(csvfile)
            # Preserves header order so we can write CSV back later
            fieldnames = reader.fieldnames
            # Iterate through each row to check whether there is a correctly-formatted end date (call row["end_date"]) and leader, if not add the wholerow to updated_rows
            for row in reader:
                try:
                    end_dt = datetime.datetime.strptime(row["end_date"], "%d/%m/%Y")
                except (ValueError, TypeError):
                    updated_rows.append(row)
                    continue

                leader_text = str(row.get("scout_leader", "") or "").strip()
                leader_lower = leader_text.lower()

                if leader_lower in ("", "na"):
                    if leader_lower != "unassigned":
                        row["scout_leader"] = "unassigned"
                        changed = True
                    updated_rows.append(row)
                    continue

                if leader_lower == "unassigned":
                    updated_rows.append(row)
                    continue

                if end_dt + datetime.timedelta(days=1) < now:
                    row["scout_leader"] = "unassigned"
                    changed = True

                updated_rows.append(row)

        # Ensure we only rewrite CSV (completely rewrite since in "w" mode) if something changed and we know header names
        if changed and fieldnames:
            with open(CAMPS_FILE, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(updated_rows)
            return True
    except FileNotFoundError:
        messagebox.showerror("Missing data", f"Could not find {CAMPS_FILE}.")
    return False


"""Reload the leader's assigned camps from camps.csv file for any potential supervision updates"""
def refresh_leader_camps():
    global camp_dict
    camp_dict = selected_leader.load_camps_for_leader(CAMPS_FILE)

release_completed_camps()
refresh_leader_camps()


"""Return the set of map locations that currently have no supervising leader."""
def locations_with_unassigned_camps():
    locations = set()
    try:
        with open(CAMPS_FILE, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                leader_value = str(row.get("scout_leader", "") or "").strip().lower()
                if leader_value != "unassigned":
                    continue
                # Extract the "location" column value for that row with an empty("or NA") leader
                loc = row.get("location")
                if loc:
                    locations.add(loc)
    except FileNotFoundError:
        messagebox.showerror("Missing data", f"Could not find {CAMPS_FILE}.")
    return locations


"""Within a specific location (eg: "Timimoun") return the list of camps there 
(leader-specific from camp_dict and unassigned camps)."""
def camps_for_location(location):
    # Remember camp_dict is global and contains the selected leader's camps
    camps = [camp for camp in camp_dict.values() if camp.location == location]

    try:
        with open(CAMPS_FILE, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                leader_value_raw = row.get("scout_leader", "")
                leader_value = str(leader_value_raw or "").strip()
                if leader_value.lower() != "unassigned":
                    continue  # already assigned to a leader (therefore not unassigned)
                if row.get("location") != location:
                    continue # different location to requested
                if row.get("name") in camp_dict:
                    continue # already in leader's camps

                try:
                    start_dt = datetime.datetime.strptime(row["start_date"], "%d/%m/%Y")
                    end_dt = datetime.datetime.strptime(row["end_date"], "%d/%m/%Y")
                except (ValueError, TypeError):
                    continue

                camp_obj = SimpleNamespace(
                    name=row["name"],
                    location=row["location"],
                    type=row.get("type", ""),
                    start_date=start_dt,
                    end_date=end_dt,
                    food_supply_per_day=int(row.get("food_supply_per_day", 0) or 0),
                    food_demand_per_day=int(row.get("food_demand_per_day", 0) or 0),
                    scout_leader=leader_value,
                    pay=float(row.get("pay", 0) or 0),
                )
                camps.append(camp_obj)
    except FileNotFoundError:
        messagebox.showerror("Missing data", f"Could not find {CAMPS_FILE}.")

    return camps


"""Time status of a camp: planned, ongoing, completed."""
def get_camp_status(camp, now=None):
    # Default parameter is current datetime if not provided (if provided will use inputted value to calculate status)
    if now is None:
        now = datetime.datetime.now()

    if camp.start_date > now:
        return "planned" # start_date is in the future

    if camp.end_date + datetime.timedelta(days=1) < now:
        return "completed" # compeleted since end date + 1 day grace period has passed

    return "ongoing" # camp is currently ongoing


"""Check if a camp is unassigned (no scout leader), extracts from the "scout_leader" attribute of 
the camp object created in camps_for_location(), meaning this function is used upon clicking on 
individual camps (the treeview knows which camp is unsupervised from camps_for_location() - CSV "scout_leader" lookup)."""
def is_unassigned(camp):
    leader_value = getattr(camp, "scout_leader", "")
    if leader_value is None:
        return False
    return str(leader_value).strip().lower() == "unassigned"




"""
show_others(): Show the 3 main frames of the main GUI after the welcome animation and board slide-downs are complete
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
            show_camps_treeview()
            show_create_camp_window()

    # Hover event functions for tent icons
    def on_enter(item):

        mapsubcanvas.itemconfig(item, image=mapsubcanvas.tent_highlighted)

    def on_leave(item):

        mapsubcanvas.itemconfig(item, image=mapsubcanvas.tent)

    # Attaches three behaviors (click, hover-enter, hover-leave) to one specific tent icon on the canvas
    def create_bind(item):
        mapsubcanvas.tag_bind(item, "<Button-1>", lambda event: on_click(event, item))
        mapsubcanvas.tag_bind(item, "<Enter>", lambda event: (on_enter(item)))
        mapsubcanvas.tag_bind(item, "<Leave>", lambda event: (on_leave(item)))


    """ CAMP Treeview FRAME: Placing a camp_treeview frame on the Message Board, then placing a 
    treeview widget inside the frame to display all camps at that location """
    camps_treeview_subframe = tk.Frame(canvas, width=500, height=300, bg="white")
    camps_treeview_window = canvas.create_window(320,525, window = camps_treeview_subframe, width=500, height=300)
    # Label for the camp treeview
    camps_listtitle = tk.Label(camps_treeview_subframe, text="Camps at this location:", font=("Comic Sans MS", 12), bg="white", fg="black")
    camps_listtitle.pack()
    # Creating the treeview widget itself
    camps_treeview = ttk.Treeview(camps_treeview_subframe, columns=("Camp Name", "Status"), show="headings")
    camps_treeview.heading("Camp Name", text="Camp Name")
    camps_treeview.heading("Status", text="Status")
    camps_treeview.column("Camp Name", width=100, anchor='center')
    camps_treeview.column("Status", width=100, anchor='center')
    camps_treeview.pack(expand=True, fill="both")
    # Initial treeview state is hidden until a tent icon is clicked
    canvas.itemconfigure(camps_treeview_window, state="hidden")

    camp_rows_by_name = {}

    """Runs when a camp row is clicked in the treeview"""
    def on_camp_row_click(event):
        # Get the row ID (Y coordinate of the click) that was clicked
        row_id = camps_treeview.identify_row(event.y)
        if not row_id:
            return  # clicked outside any row
        # Extract the tuple of column values stored in that row (Values are "Camp Name", "Status")
        values = camps_treeview.item(row_id, "values")
        camp_name = values[0] if values else ""
        if not camp_name or camp_name == "No camps yet":
            return

        camp_obj = camp_rows_by_name.get(camp_name)
        if not camp_obj:
            messagebox.showerror("Camp missing", f"Couldn't find details for {camp_name}.")
            return

        camp_status = get_camp_status(camp_obj)
        show_create_camp_window(camp_obj)

        # If unassigned, offer to assign the selected leader as supervising leader
        if is_unassigned(camp_obj):
            if messagebox.askyesno("Confirm supervision", f"Become the supervising leader for '{camp_name}'?"):
                result = selected_leader.select_camp(camp_name)
                if result.get("success"):
                    if camp_status == "completed":
                        messagebox.showinfo(
                            "Assignment blocked",
                            "You cannot assign yourself to a completed camp."
                        )
                    else:
                        messagebox.showinfo("Camp assigned", result.get("message", "You now supervise this camp."))
                    refresh_leader_camps()
                    show_camps_treeview()
                else:
                    messagebox.showerror("Unable to assign", result.get("message", "Assignment failed."))
            return

        messagebox.showinfo(
            camp_name,
            f"Location: {camp_obj.location}\n"
            f"Starts: {camp_obj.start_date.strftime('%Y/%m/%d')}\n"
            f"Ends: {camp_obj.end_date.strftime('%Y/%m/%d')}\n"
            f"Status: {camp_status.title()}"
        )

    # event is ButtonRelease-1 to avoid conflict with row selection
    camps_treeview.bind("<ButtonRelease-1>", on_camp_row_click)
    
    # Initial treeview state is hidden until a tent icon is clicked
    def show_camps_treeview():
        nonlocal camp_rows_by_name
        canvas.itemconfigure(msg_window, state="hidden")
        canvas.itemconfigure(camps_treeview_window, state="normal")
        canvas.tag_raise(camps_treeview_window)
        canvas.update_idletasks()
        # Update CSV data to release completed camps back to "unassigned" before showing
        release_completed_camps()
        # Refreshes camp_dict for the leader
        refresh_leader_camps()
        # Clear existing treeview rows (children)
        for item in camps_treeview.get_children():
            camps_treeview.delete(item)

        # Calls camps_for_location to get camps at the current location and appends to camp_rows_by_name
        camps_at_location = camps_for_location(current_location)
        camp_rows_by_name = {camp.name: camp for camp in camps_at_location}

        if not camps_at_location:
            camps_treeview.insert("", "end", values=("No camps yet", "--"))
            return

        # For each camp at the location, determine status and insert into treeview
        now = datetime.datetime.now()
        for camp in camps_at_location:
            camp_status = get_camp_status(camp, now)

            if is_unassigned(camp):
                if camp_status == "completed":
                    status_label = "Completed"
                else:
                    status_label = "Unassigned"
            else:
                status_label = camp_status.title()

            camps_treeview.insert("", "end", values=(camp.name, status_label))


    """ INDIVIDUAL CAMP & ITS ACTIVITIES FRAME AND WINDOW: triggers upon clicking and entering a camp on camp treeview """
    createcampframe = tk.Frame(canvas, background="lightblue")
    createcampframe.grid_columnconfigure(0, weight=1)
    createcampframe.grid_columnconfigure(1, weight=1)
    createcampframe.grid_columnconfigure(2, weight=1)

    create_camp_window = canvas.create_window(960, 400, window=createcampframe, width=500, height=500)
    canvas.itemconfigure(create_camp_window, state="hidden")

    # Create a second frame which is inner to createcampframe to cater to each camp activity details (quick access and wipe)
    makecampframe = tk.Frame(createcampframe, background="lightblue")
    makecampframe.pack(expand=True, fill="both", padx=10, pady=10)

    def show_create_camp_window(camp_obj=None):
        canvas.itemconfigure(create_camp_window, state="normal")
        canvas.itemconfigure(map_window, state="hidden")
        for widget in makecampframe.winfo_children():
            widget.destroy()

        #canvas.itemconfigure(create_camp_window, state="normal")
        #canvas.itemconfigure(map_window, state="hidden")
        #for widget in makecampframe.winfo_children():
        #    widget.destroy()


        #for widget in makecampframe.winfo_children():
        #    widget.destroy()

        canvas.itemconfigure(create_camp_window, state="normal")
        canvas.itemconfigure(map_window, state="hidden")
        canvas.tag_raise(create_camp_window)
        canvas.update_idletasks()

        for i in range(3):
            makecampframe.grid_columnconfigure(i, weight=1)

        tk.Label(
            makecampframe,
            text=f"Camp name: {camp_obj.name}",
            bg="dodgerblue",
            font=("Comic Sans MS", 22)
        ).grid(row=0, column=0, columnspan=3, sticky='ew', padx=10, pady=(10, 5))

        def placeholder_function():
            print("Hello World!")

        def open_add_campers_window():
            """Window to bulk add unassigned campers to the camp"""
            add_window = tk.Toplevel()
            add_window.title(f"Add Campers to {camp_obj.name}")
            add_window.geometry("500x600")
            add_window.configure(bg="lightblue")
            
            add_window.grid_columnconfigure(0, weight=1)
            add_window.grid_rowconfigure(2, weight=1)
            
            # Title
            title_label = tk.Label(add_window, text=f"Add Campers to {camp_obj.name}",
                                  bg="dodgerblue", fg="white", font=("Comic Sans MS", 14, "bold"))
            title_label.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))
            
            # Get all campers from CSV
            df_campers = pd.read_csv("data/campers.csv", index_col="camper_id")
            
            # Filter to only unassigned campers (camps = "Na" or empty)
            unassigned_campers = []
            for camper_id, row in df_campers.iterrows():
                camp_val = row.get("camps", "")
                if pd.isna(camp_val) or str(camp_val).strip() in ("", "Na"):
                    unassigned_campers.append({
                        "id": str(camper_id),
                        "name": f"{row['first_name']} {row['last_name']}",
                        "age": row['age']
                    })
            
            # Dictionary to track checkbox states
            selected_campers = {}
            
            if not unassigned_campers:
                no_campers = tk.Label(add_window, text="No unassigned campers available",
                                     bg="white", fg="black", font=("Comic Sans MS", 12))
                no_campers.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
            else:
                # Scrollable treeview with checkboxes
                tree_frame = tk.Frame(add_window, bg="white")
                tree_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
                
                scrollbar = ttk.Scrollbar(tree_frame)
                scrollbar.pack(side="right", fill="y")
                
                campers_tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Age"), 
                                           show="tree headings", yscrollcommand=scrollbar.set)
                scrollbar.config(command=campers_tree.yview)
                
                campers_tree.heading("#0", text="✓")
                campers_tree.heading("ID", text="ID")
                campers_tree.heading("Name", text="Name")
                campers_tree.heading("Age", text="Age")
                
                campers_tree.column("#0", width=30)
                campers_tree.column("ID", width=40)
                campers_tree.column("Name", width=200)
                campers_tree.column("Age", width=50)
                
                # Insert campers as rows
                for camper in unassigned_campers:
                    camper_id = camper["id"]
                    selected_campers[camper_id] = False
                    campers_tree.insert("", "end", text="☐", values=(camper_id, camper["name"], camper["age"]))
                
                # Click to toggle checkbox
                def on_tree_click(event):
                    item = campers_tree.identify_row(event.y)
                    if not item:
                        return
                    col = campers_tree.identify_column(event.x)
                    if col == "#0":  # Checkbox column
                        values = campers_tree.item(item, "values")
                        camper_id = values[0]
                        # Toggle selection
                        selected_campers[camper_id] = not selected_campers[camper_id]
                        checkbox_text = "☑" if selected_campers[camper_id] else "☐"
                        campers_tree.item(item, text=checkbox_text)
                
                campers_tree.bind("<Button-1>", on_tree_click)
                campers_tree.pack(fill="both", expand=True)
            
            # Button frame
            button_frame = tk.Frame(add_window, bg="lightblue")
            button_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
            button_frame.grid_columnconfigure(0, weight=1)
            button_frame.grid_columnconfigure(1, weight=1)
            
            # Select All / Deselect All buttons
            def select_all():
                for camper_id in selected_campers:
                    selected_campers[camper_id] = True
                for item in campers_tree.get_children():
                    campers_tree.item(item, text="☑")
            
            def deselect_all():
                for camper_id in selected_campers:
                    selected_campers[camper_id] = False
                for item in campers_tree.get_children():
                    campers_tree.item(item, text="☐")
            
            ttk.Button(button_frame, text="Select All", command=select_all).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            ttk.Button(button_frame, text="Deselect All", command=deselect_all).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            
            # Confirm button
            def confirm_add():
                selected_ids = [int(cid) for cid, selected in selected_campers.items() if selected]
                if not selected_ids:
                    messagebox.showwarning("No selection", "Please select at least one camper to add.")
                    return
                
                try:
                    for camper_id in selected_ids:
                        result = selected_leader.assign_camper(camper_id, camp_obj.name)
                        if not result.get("success"):
                            messagebox.showerror("Assignment failed", result.get("message", "Unknown error"))
                            return
                    
                    messagebox.showinfo("Success", f"Added {len(selected_ids)} camper(s) to {camp_obj.name}")
                    add_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to add campers: {str(e)}")
            
            confirm_btn = tk.Button(button_frame, text="Add Selected Campers", command=confirm_add, 
                                   bg="green", fg="black", font=("Comic Sans MS", 12, "bold"),
                                   activebackground="darkgreen", activeforeground="white",
                                   relief="raised", bd=2)
            confirm_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="ew", ipady=8)

        def open_remove_campers_window():
            """Window to bulk remove campers from the camp"""
            remove_window = tk.Toplevel()
            remove_window.title(f"Remove Campers from {camp_obj.name}")
            remove_window.geometry("500x600")
            remove_window.configure(bg="lightblue")
            
            remove_window.grid_columnconfigure(0, weight=1)
            remove_window.grid_rowconfigure(2, weight=1)
            
            # Title
            title_label = tk.Label(remove_window, text=f"Remove Campers from {camp_obj.name}",
                                  bg="dodgerblue", fg="white", font=("Comic Sans MS", 14, "bold"))
            title_label.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))
            
            # Get campers currently in this camp
            df_campers = pd.read_csv("data/campers.csv", index_col="camper_id")
            
            camp_campers = []
            for camper_id, row in df_campers.iterrows():
                if row.get("camps") == camp_obj.name:
                    camp_campers.append({
                        "id": str(camper_id),
                        "name": f"{row['first_name']} {row['last_name']}",
                        "age": row['age']
                    })
            
            # Dictionary to track checkbox states
            selected_campers = {}
            
            if not camp_campers:
                no_campers = tk.Label(remove_window, text="No campers assigned to this camp",
                                     bg="white", fg="black", font=("Comic Sans MS", 12))
                no_campers.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
            else:
                # Scrollable treeview with checkboxes
                tree_frame = tk.Frame(remove_window, bg="white")
                tree_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
                
                scrollbar = ttk.Scrollbar(tree_frame)
                scrollbar.pack(side="right", fill="y")
                
                campers_tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Age"), 
                                           show="tree headings", yscrollcommand=scrollbar.set)
                scrollbar.config(command=campers_tree.yview)
                
                campers_tree.heading("#0", text="✓")
                campers_tree.heading("ID", text="ID")
                campers_tree.heading("Name", text="Name")
                campers_tree.heading("Age", text="Age")
                
                campers_tree.column("#0", width=30)
                campers_tree.column("ID", width=40)
                campers_tree.column("Name", width=200)
                campers_tree.column("Age", width=50)
                
                # Insert campers as rows
                for camper in camp_campers:
                    camper_id = camper["id"]
                    selected_campers[camper_id] = False
                    campers_tree.insert("", "end", text="☐", values=(camper_id, camper["name"], camper["age"]))
                
                # Click to toggle checkbox
                def on_tree_click(event):
                    item = campers_tree.identify_row(event.y)
                    if not item:
                        return
                    col = campers_tree.identify_column(event.x)
                    if col == "#0":  # Checkbox column
                        values = campers_tree.item(item, "values")
                        camper_id = values[0]
                        # Toggle selection
                        selected_campers[camper_id] = not selected_campers[camper_id]
                        checkbox_text = "☑" if selected_campers[camper_id] else "☐"
                        campers_tree.item(item, text=checkbox_text)
                
                campers_tree.bind("<Button-1>", on_tree_click)
                campers_tree.pack(fill="both", expand=True)
            
            # Button frame
            button_frame = tk.Frame(remove_window, bg="lightblue")
            button_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
            button_frame.grid_columnconfigure(0, weight=1)
            button_frame.grid_columnconfigure(1, weight=1)
            
            # Select All / Deselect All buttons
            def select_all():
                for camper_id in selected_campers:
                    selected_campers[camper_id] = True
                for item in campers_tree.get_children():
                    campers_tree.item(item, text="☑")
            
            def deselect_all():
                for camper_id in selected_campers:
                    selected_campers[camper_id] = False
                for item in campers_tree.get_children():
                    campers_tree.item(item, text="☐")
            
            ttk.Button(button_frame, text="Select All", command=select_all).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            ttk.Button(button_frame, text="Deselect All", command=deselect_all).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            
            # Confirm button
            def confirm_remove():
                selected_ids = [int(cid) for cid, selected in selected_campers.items() if selected]
                if not selected_ids:
                    messagebox.showwarning("No selection", "Please select at least one camper to remove.")
                    return
                
                try:
                    for camper_id in selected_ids:
                        result = selected_leader.remove_camper(camper_id)
                        if not result.get("success"):
                            messagebox.showerror("Removal failed", result.get("message", "Unknown error"))
                            return
                    
                    messagebox.showinfo("Success", f"Removed {len(selected_ids)} camper(s) from {camp_obj.name}")
                    remove_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to remove campers: {str(e)}")
            
            confirm_btn = tk.Button(button_frame, text="Remove Selected Campers", command=confirm_remove, 
                                   bg="red", fg="black", font=("Comic Sans MS", 12, "bold"),
                                   activebackground="darkred", activeforeground="white",
                                   relief="raised", bd=2)
            confirm_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="ew", ipady=8)

        # New window to show campers for each activity
                # New window to show campers for each activity
        def open_activity_window(activity_name):
            activity_window = tk.Toplevel()
            activity_window.title(f"Campers for {activity_name}")
            activity_window.geometry("500x500")

            activity_window.configure(bg="lightblue")

            activity_window.grid_columnconfigure(0, weight=1)
            activity_window.grid_columnconfigure(1, weight=1)
            activity_window.grid_rowconfigure(1, weight=1)

            activity_window_title = tk.Label(activity_window, text=f"Campers assigned to {activity_name}",
                                             bg="dodgerblue", font=("Comic Sans MS", 20), fg="white")
            activity_window_title.grid(row=0, column=0, columnspan=2, sticky='ew', padx=10, pady=(10, 5))

            df = leaders[placeholder].get_campers_for_activity(camp_obj.name)
            df = df.set_index("activity_name")
            assigned_campers = df.loc[activity_name, "assigned_campers"]

            if pd.isna(assigned_campers) or assigned_campers == "":
                assigned_campers_list = []
            elif isinstance(assigned_campers, str):
                assigned_campers_list = [x.strip() for x in assigned_campers.split(",")]
            else:
                assigned_campers_list = assigned_campers

            if not assigned_campers_list:
                no_campers_label = tk.Label(activity_window, text="No campers assigned",
                                            bg="white", fg="black", font=("Comic Sans MS", 16))
                no_campers_label.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(5, 10))
            else:
                df_names = leaders[placeholder].get_camper_id_to_names(assigned_campers_list)

                tree_frame = tk.Frame(activity_window)
                tree_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

                campers_tree = ttk.Treeview(tree_frame, columns=list(df_names.columns), show="headings")
                campers_tree.pack(fill="both", expand=True)

                for col in df_names.columns:
                    campers_tree.heading(col, text=col)
                    campers_tree.column(col, anchor='center')

                for _, row in df_names.iterrows():
                    campers_tree.insert("", "end", values=list(row))

            # Get activity_id from activity_name
            df_activities = pd.read_csv("data/activities.csv")
            activity_row = df_activities[df_activities["activity_name"] == activity_name]
            if activity_row.empty or camp_obj.name not in activity_row["camp_name"].values:
                messagebox.showerror("Error", f"Activity {activity_name} not found in camp {camp_obj.name}")
                return
            activity_id = activity_row.iloc[0]["activity_id"]

            # Add campers to activity window
            def open_add_activity_window():
                add_act_window = tk.Toplevel()
                add_act_window.title(f"Add Campers to {activity_name}")
                add_act_window.geometry("500x600")
                add_act_window.configure(bg="lightblue")
                
                add_act_window.grid_columnconfigure(0, weight=1)
                add_act_window.grid_rowconfigure(2, weight=1)
                
                # Title
                title_label = tk.Label(add_act_window, text=f"Add Campers to {activity_name}",
                                      bg="dodgerblue", fg="white", font=("Comic Sans MS", 14, "bold"))
                title_label.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))
                
                # Get campers assigned to this camp (only those in camp_obj.name)
                df_campers = pd.read_csv("data/campers.csv", index_col="camper_id")
                
                # Get already assigned campers to this activity
                already_assigned = set([int(c.strip()) for c in str(assigned_campers).split(",")]) if assigned_campers_list else set()
                
                # Filter to campers in this camp but NOT already in this activity
                available_campers = []
                for camper_id, row in df_campers.iterrows():
                    if row.get("camps") == camp_obj.name and camper_id not in already_assigned:
                        available_campers.append({
                            "id": str(camper_id),
                            "name": f"{row['first_name']} {row['last_name']}",
                            "age": row['age']
                        })
                
                selected_campers = {}
                
                if not available_campers:
                    no_campers = tk.Label(add_act_window, text="No available campers in this camp",
                                         bg="white", fg="black", font=("Comic Sans MS", 12))
                    no_campers.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
                else:
                    tree_frame = tk.Frame(add_act_window, bg="white")
                    tree_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
                    
                    scrollbar = ttk.Scrollbar(tree_frame)
                    scrollbar.pack(side="right", fill="y")
                    
                    campers_tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Age"), 
                                               show="tree headings", yscrollcommand=scrollbar.set)
                    scrollbar.config(command=campers_tree.yview)
                    
                    campers_tree.heading("#0", text="✓")
                    campers_tree.heading("ID", text="ID")
                    campers_tree.heading("Name", text="Name")
                    campers_tree.heading("Age", text="Age")
                    
                    campers_tree.column("#0", width=30)
                    campers_tree.column("ID", width=40)
                    campers_tree.column("Name", width=200)
                    campers_tree.column("Age", width=50)
                    
                    for camper in available_campers:
                        camper_id = camper["id"]
                        selected_campers[camper_id] = False
                        campers_tree.insert("", "end", text="☐", values=(camper_id, camper["name"], camper["age"]))
                    
                    def on_tree_click(event):
                        item = campers_tree.identify_row(event.y)
                        if not item:
                            return
                        col = campers_tree.identify_column(event.x)
                        if col == "#0":
                            values = campers_tree.item(item, "values")
                            camper_id = values[0]
                            selected_campers[camper_id] = not selected_campers[camper_id]
                            checkbox_text = "☑" if selected_campers[camper_id] else "☐"
                            campers_tree.item(item, text=checkbox_text)
                    
                    campers_tree.bind("<Button-1>", on_tree_click)
                    campers_tree.pack(fill="both", expand=True)
                
                # Button frame
                button_frame = tk.Frame(add_act_window, bg="lightblue")
                button_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
                button_frame.grid_columnconfigure(0, weight=1)
                button_frame.grid_columnconfigure(1, weight=1)
                
                def select_all():
                    for camper_id in selected_campers:
                        selected_campers[camper_id] = True
                    for item in campers_tree.get_children():
                        campers_tree.item(item, text="☑")
                
                def deselect_all():
                    for camper_id in selected_campers:
                        selected_campers[camper_id] = False
                    for item in campers_tree.get_children():
                        campers_tree.item(item, text="☐")
                
                ttk.Button(button_frame, text="Select All", command=select_all).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
                ttk.Button(button_frame, text="Deselect All", command=deselect_all).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
                
                def confirm_add_activity():
                    selected_ids = [int(cid) for cid, selected in selected_campers.items() if selected]
                    if not selected_ids:
                        messagebox.showwarning("No selection", "Please select at least one camper to add.")
                        return
                    
                    try:
                        result = selected_leader.assign_campers_to_activity(activity_id, selected_ids)
                        if not result.get("success"):
                            messagebox.showerror("Assignment failed", result.get("message", "Unknown error"))
                            return
                        
                        messagebox.showinfo("Success", f"Added {len(selected_ids)} camper(s) to {activity_name}")
                        add_act_window.destroy()
                        activity_window.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to add campers: {str(e)}")
                
                confirm_btn = tk.Button(button_frame, text="Add Selected Campers", command=confirm_add_activity, 
                                       bg="green", fg="black", font=("Comic Sans MS", 12, "bold"),
                                       activebackground="darkgreen", activeforeground="white",
                                       relief="raised", bd=2)
                confirm_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="ew", ipady=8)

            # Remove campers from activity window
            def open_remove_activity_window():
                remove_act_window = tk.Toplevel()
                remove_act_window.title(f"Remove Campers from {activity_name}")
                remove_act_window.geometry("500x600")
                remove_act_window.configure(bg="lightblue")
                
                remove_act_window.grid_columnconfigure(0, weight=1)
                remove_act_window.grid_rowconfigure(2, weight=1)
                
                # Title
                title_label = tk.Label(remove_act_window, text=f"Remove Campers from {activity_name}",
                                      bg="dodgerblue", fg="white", font=("Comic Sans MS", 14, "bold"))
                title_label.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))
                
                selected_campers = {}
                
                if not assigned_campers_list:
                    no_campers = tk.Label(remove_act_window, text="No campers assigned to this activity",
                                         bg="white", fg="black", font=("Comic Sans MS", 12))
                    no_campers.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
                else:
                    df_campers = pd.read_csv("data/campers.csv", index_col="camper_id")
                    
                    # Build list of assigned campers with their details
                    assigned_details = []
                    for camper_id in assigned_campers_list:
                        try:
                            camper_int = int(camper_id)
                            if camper_int in df_campers.index:
                                row = df_campers.loc[camper_int]
                                assigned_details.append({
                                    "id": str(camper_int),
                                    "name": f"{row['first_name']} {row['last_name']}",
                                    "age": row['age']
                                })
                        except (ValueError, KeyError):
                            continue
                    
                    tree_frame = tk.Frame(remove_act_window, bg="white")
                    tree_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
                    
                    scrollbar = ttk.Scrollbar(tree_frame)
                    scrollbar.pack(side="right", fill="y")
                    
                    campers_tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Age"), 
                                               show="tree headings", yscrollcommand=scrollbar.set)
                    scrollbar.config(command=campers_tree.yview)
                    
                    campers_tree.heading("#0", text="✓")
                    campers_tree.heading("ID", text="ID")
                    campers_tree.heading("Name", text="Name")
                    campers_tree.heading("Age", text="Age")
                    
                    campers_tree.column("#0", width=30)
                    campers_tree.column("ID", width=40)
                    campers_tree.column("Name", width=200)
                    campers_tree.column("Age", width=50)
                    
                    for camper in assigned_details:
                        camper_id = camper["id"]
                        selected_campers[camper_id] = False
                        campers_tree.insert("", "end", text="☐", values=(camper_id, camper["name"], camper["age"]))
                    
                    def on_tree_click(event):
                        item = campers_tree.identify_row(event.y)
                        if not item:
                            return
                        col = campers_tree.identify_column(event.x)
                        if col == "#0":
                            values = campers_tree.item(item, "values")
                            camper_id = values[0]
                            selected_campers[camper_id] = not selected_campers[camper_id]
                            checkbox_text = "☑" if selected_campers[camper_id] else "☐"
                            campers_tree.item(item, text=checkbox_text)
                    
                    campers_tree.bind("<Button-1>", on_tree_click)
                    campers_tree.pack(fill="both", expand=True)
                
                # Button frame
                button_frame = tk.Frame(remove_act_window, bg="lightblue")
                button_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
                button_frame.grid_columnconfigure(0, weight=1)
                button_frame.grid_columnconfigure(1, weight=1)
                
                def select_all():
                    for camper_id in selected_campers:
                        selected_campers[camper_id] = True
                    for item in campers_tree.get_children():
                        campers_tree.item(item, text="☑")
                
                def deselect_all():
                    for camper_id in selected_campers:
                        selected_campers[camper_id] = False
                    for item in campers_tree.get_children():
                        campers_tree.item(item, text="☐")
                
                ttk.Button(button_frame, text="Select All", command=select_all).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
                ttk.Button(button_frame, text="Deselect All", command=deselect_all).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
                
                def confirm_remove_activity():
                    selected_ids = [int(cid) for cid, selected in selected_campers.items() if selected]
                    if not selected_ids:
                        messagebox.showwarning("No selection", "Please select at least one camper to remove.")
                        return
                    
                    try:
                        result = selected_leader.remove_campers_from_activity(activity_id, selected_ids)
                        if not result.get("success"):
                            messagebox.showerror("Removal failed", result.get("message", "Unknown error"))
                            return
                        
                        messagebox.showinfo("Success", f"Removed {len(selected_ids)} camper(s) from {activity_name}")
                        remove_act_window.destroy()
                        activity_window.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to remove campers: {str(e)}")
                
                confirm_btn = tk.Button(button_frame, text="Remove Selected Campers", command=confirm_remove_activity, 
                                       bg="red", fg="black", font=("Comic Sans MS", 12, "bold"),
                                       activebackground="darkred", activeforeground="white",
                                       relief="raised", bd=2)
                confirm_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="ew", ipady=8)

            # Button frame for add/remove
            button_frame = tk.Frame(activity_window, bg="lightblue")
            button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))
            button_frame.grid_columnconfigure(0, weight=1)
            button_frame.grid_columnconfigure(1, weight=1)
            
            add_act_btn = tk.Button(button_frame, text="Add Campers", command=open_add_activity_window, 
                                   bg="green", fg="black", font=("Comic Sans MS", 12, "bold"),
                                   activebackground="darkgreen", activeforeground="white",
                                   relief="raised", bd=2)
            add_act_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew", ipady=5)
            
            remove_act_btn = tk.Button(button_frame, text="Remove Campers", command=open_remove_activity_window, 
                                      bg="red", fg="black", font=("Comic Sans MS", 12, "bold"),
                                      activebackground="darkred", activeforeground="white",
                                      relief="raised", bd=2)
            remove_act_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew", ipady=5)
        
        def open_extra_notes_window(activity_name):
                activity_window = tk.Toplevel()
                activity_window.title(f"Extra notes for {activity_name}")
                activity_window.geometry("400x400")

                activity_window.configure(bg="lightblue")

                activity_window.grid_columnconfigure(0, weight=1)
                activity_window.grid_rowconfigure(1, weight=1)

                activity_window_title = tk.Label(activity_window, text=f"Extra notes for {activity_name}",
                                                 bg="dodgerblue", font=("Comic Sans MS", 22))
                activity_window_title.grid(row=0, column=0, columnspan=2, sticky='ew', padx=10, pady=(10, 5))

                df = leaders[placeholder].get_notes_for_activity(camp_obj.name)

                # Filter only by activity_name
                df_activity = df[df["activity_name"] == activity_name]

                tree_frame = tk.Frame(activity_window)
                tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

                campers_tree = ttk.Treeview(tree_frame, columns=["activity_name", "extra_notes"], show="headings")
                campers_tree.pack(fill="both", expand=True)

                campers_tree.heading("activity_name", text="Activity Name")
                campers_tree.heading("extra_notes", text="Extra Notes")
                campers_tree.column("activity_name", anchor='center')
                campers_tree.column("extra_notes", anchor='center')

                # Insert all rows, replacing empty notes with placeholder
                for _, row in df_activity.iterrows():
                    notes = row["extra_notes"]
                    if pd.isna(notes) or notes == "":
                        notes = "No notes added"
                    campers_tree.insert("", "end", values=[row["activity_name"], notes])

        activity_label = tk.Label(makecampframe, text="Activities", bg="dodgerblue", font=("Comic Sans MS", 18))
        activity_label.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=(5, 10))

        hiking_label = tk.Label(makecampframe, text="Hiking", bg="white", fg="black", font=("Comic Sans MS", 18))
        hiking_label.grid(row=2, column=0, sticky="ew", padx=10, pady=(10, 5))

        view_hiking_camps = tk.Button(makecampframe, text="View Campers",
                                      command=lambda: open_activity_window("Hiking"), bg="white",
                                      font=("Comic Sans MS", 18))
        view_hiking_camps.grid(row=2, column=1, sticky="ew", padx=10, pady=(10, 5))

        hiking_notes = tk.Button(makecampframe, text="Notes", command=lambda: open_extra_notes_window("Hiking"), bg="white",
                                 font=("Comic Sans MS", 18))
        hiking_notes.grid(row=2, column=2, sticky="ew", padx=10, pady=(10, 5))

        archery_label = tk.Label(makecampframe, text="Archery", bg="white", fg="black", font=("Comic Sans MS", 18))
        archery_label.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 5))

        view_archery_camps = tk.Button(makecampframe, text="View Campers",
                                       command=lambda: open_activity_window("Archery"), bg="white",
                                       font=("Comic Sans MS", 18))
        view_archery_camps.grid(row=3, column=1, sticky="ew", padx=10, pady=(5, 5))

        archery_notes = tk.Button(makecampframe, text="Notes", command=lambda: open_extra_notes_window("Archery"), bg="white",
                                  font=("Comic Sans MS", 18))
        archery_notes.grid(row=3, column=2, sticky="ew", padx=10, pady=(5, 5))

        campfire_label = tk.Label(makecampframe, text="Campfire", bg="white", fg="black", font=("Comic Sans MS", 18))
        campfire_label.grid(row=4, column=0, sticky="ew", padx=10, pady=(5, 5))

        view_campfire_camps = tk.Button(makecampframe, text="View Campers",
                                        command=lambda: open_activity_window("Campfire"), bg="white",
                                        font=("Comic Sans MS", 18))
        view_campfire_camps.grid(row=4, column=1, sticky="ew", padx=10, pady=(5, 5))

        campfire_notes = tk.Button(makecampframe, text="Notes", command=lambda: open_extra_notes_window("Campfire"), bg="white",
                                   font=("Comic Sans MS", 18))
        campfire_notes.grid(row=4, column=2, sticky="ew", padx=10, pady=(5, 5))

        rock_climbing_label = tk.Label(makecampframe, text="Rock Climbing", bg="white", fg="black",
                                       font=("Comic Sans MS", 18))
        rock_climbing_label.grid(row=5, column=0, sticky="ew", padx=10, pady=(5, 10))

        view_rock_climbing_camps = tk.Button(makecampframe, text="View Campers",
                                             command=lambda: open_activity_window("Rock Climbing"), bg="white",
                                             font=("Comic Sans MS", 18))
        view_rock_climbing_camps.grid(row=5, column=1, sticky="ew", padx=10, pady=(5, 10))

        rock_climbing_notes = tk.Button(makecampframe, text="Notes", command=lambda: open_extra_notes_window("Rock Climbing"), bg="white",
                                        font=("Comic Sans MS", 18))
        rock_climbing_notes.grid(row=5, column=2, sticky="ew", padx=10, pady=(5, 10))

         # Campers section
        campers_label = tk.Label(makecampframe, text="Campers", bg="dodgerblue", font=("Comic Sans MS", 18))
        campers_label.grid(row=6, column=0, columnspan=3, sticky="ew", padx=10, pady=(5, 10))

        add_campers_label = tk.Label(makecampframe, text="Add Campers", bg="white", fg="black", font=("Comic Sans MS", 18))
        add_campers_label.grid(row=7, column=0, sticky="ew", padx=10, pady=(10, 5))

        add_campers_button = tk.Button(makecampframe, text="Add to Camp",
                                       command=open_add_campers_window, bg="white",
                                       font=("Comic Sans MS", 18))
        add_campers_button.grid(row=7, column=1, columnspan=2, sticky="ew", padx=10, pady=(10, 5))

        remove_campers_label = tk.Label(makecampframe, text="Remove Campers", bg="white", fg="black", font=("Comic Sans MS", 18))
        remove_campers_label.grid(row=8, column=0, sticky="ew", padx=10, pady=(5, 10))

        remove_campers_button = tk.Button(makecampframe, text="Remove from Camp",
                                          command=open_remove_campers_window, bg="white",
                                          font=("Comic Sans MS", 18))
        remove_campers_button.grid(row=8, column=1, columnspan=2, sticky="ew", padx=10, pady=(5, 10))

    # Generating tent icons on the map based on leader's camps
    positions = leaders[placeholder].create_leader_dict(camp_dict, location_coords)

    for location in locations_with_unassigned_camps():
        if location in location_coords and location not in positions:
            positions[location] = location_coords[location]

    print(positions)
    # Iterating through a leader's dictionary of camps to place tent icons on the map canvas, fill in tent_icons dict with key itemID and asscoiated tent name, and bind events
    for tent, (x,y) in positions.items():
        item = mapsubcanvas.create_image(x, y, anchor="c", image=photoimagetent)
        tent_icons[item] = tent
        create_bind(item)


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
        canvas.itemconfigure(camps_treeview_window, state="hidden")
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
    ntfsubframe = tk.Frame(canvas, width=520, height=140, bg="lightblue")
    ntfsubframe.grid_columnconfigure(0, weight=1)
    ntfsubframe.grid_columnconfigure(1, weight=1)
    ntfsubframe.grid_rowconfigure(0, weight=1)
    ntfsubframe.pack_propagate(False)
    # Styles for buttons
    style = ttk.Style()
    style.configure("Board.TButton", font=("Comic Sans MS", 16, "bold"), padding=(20, 20))
    # Button for going back to dashboard
    ttk.Button(ntfsubframe, text="Back to Dashboard",
           style="Board.TButton",
           command=show_main_dashboard).grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
    
    """statistics window function"""
    def open_statistics_window():
        stats_window = tk.Toplevel()
        stats_window.title(f"Statistics - {selected_leader.username}")
        stats_window.geometry("600x700")
        stats_window.configure(bg="lightblue")
        
        stats_window.grid_columnconfigure(0, weight=1)
        stats_window.grid_rowconfigure(1, weight=1)
        
        stats_title = tk.Label(stats_window, text=f"Statistics for {selected_leader.username}",
                              bg="dodgerblue", font=("Comic Sans MS", 18), fg="white")
        stats_title.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))
        
        """Get statistics"""
        stats_data = selected_leader.get_leader_statistics()
        
        if not stats_data.get("success"):
            no_stats_label = tk.Label(stats_window, text="No camps assigned yet",
                                     bg="white", fg="black", font=("Comic Sans MS", 14))
            no_stats_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
            return
        
        canvas_frame = tk.Canvas(stats_window, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(stats_window, orient="vertical", command=canvas_frame.yview)
        scrollable_frame = tk.Frame(canvas_frame, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_frame.configure(scrollregion=canvas_frame.bbox("all"))
        )
        
        canvas_frame.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_frame.configure(yscrollcommand=scrollbar.set)
        
        canvas_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=1, column=1, sticky="ns")
        stats_window.grid_rowconfigure(1, weight=1)
        
        # Overall stats
        overall = stats_data.get("overall", {})
        overall_frame = tk.LabelFrame(scrollable_frame, text="Overall Statistics",
                                     bg="dodgerblue", fg="white", font=("Comic Sans MS", 12, "bold"))
        overall_frame.pack(fill="x", padx=5, pady=5)
        
        overall_info = [
            f"Total Camps: {overall.get('total_camps', 0)}",
            f"Total Campers: {overall.get('total_campers', 0)}",
            f"Total Activities: {overall.get('total_activities', 0)}",
            f"Activity Utilisation: {overall.get('activity_utilisation_rate', 0)}%",
            f"Total Pay: ${overall.get('total_pay', 0)}",
            f"Food Supply: {overall.get('total_food_supply', 0)} | Demand: {overall.get('total_food_demand', 0)} | Surplus: {overall.get('food_surplus', 0)}"
        ]
        
        for info in overall_info:
            tk.Label(overall_frame, text=info, bg="dodgerblue", fg="white",
                    font=("Comic Sans MS", 10)).pack(anchor="w", padx=10, pady=2)
        
        # Per-camp stats
        camps = stats_data.get("camps", [])
        for camp in camps:
            camp_frame = tk.LabelFrame(scrollable_frame, text=f"{camp['camp_name']} - {camp['location']}",
                                      bg="lightblue", font=("Comic Sans MS", 11, "bold"))
            camp_frame.pack(fill="x", padx=5, pady=5)
            
            camp_info = [
                f"Duration: {camp['duration']}",
                f"Participation: {camp['participation']['assigned_campers']}/{camp['participation']['total_campers']} ({camp['participation']['participation_rate']}%)",
                f"Activities: {camp['activities']['total_filled']}/{camp['activities']['total_capacity']} slots ({camp['activities']['utilisation_rate']}%)",
                f"Daily Food: Supply {camp['food']['daily_supply']} | Demand {camp['food']['daily_demand']} | Surplus {camp['food']['daily_surplus']:+d}",
                f"Pay: ${camp['pay']}"
            ]
            
            for info in camp_info:
                tk.Label(camp_frame, text=info, bg="white", fg="black",
                        font=("Comic Sans MS", 9)).pack(anchor="w", padx=10, pady=1)
            
            # Comments section
            if camp.get("additional_comments"):
                comments_label = tk.Label(camp_frame, text="Comments:", bg="white", fg="black",
                                        font=("Comic Sans MS", 9, "bold"))
                comments_label.pack(anchor="w", padx=10, pady=(5, 2))
                
                for comment in camp["additional_comments"]:
                    comment_text = f"• {comment['activity_name']}: {comment['comment']}"
                    tk.Label(camp_frame, text=comment_text, bg="white", fg="black",
                            font=("Comic Sans MS", 8), wraplength=300, justify="left").pack(anchor="w", padx=20, pady=1)
    
    ttk.Button(ntfsubframe, text="View Statistics",
           style="Board.TButton",
           command=open_statistics_window).grid(row=0, column=1, sticky="nsew", padx=12, pady=12)
    
    global ntf_window
    ntf_window = canvas.create_window(320, 190, width=520, height=140, window = ntfsubframe)

    
    
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
    ttk.Button(header, text="Logout",  command = lambda: root.destroy() if messagebox.askyesno("Logout","Are you sure you want to logout?") else None).grid(row=0, column=1, sticky='e', padx=10, pady=10)

    







"""
EXECUTE THE GUI!!!
"""  
root.mainloop()
