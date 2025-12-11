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
import sys, os
sys.stderr = open(os.devnull, 'w')  


def ScoutLeaderPage(root,leader_username):
    """
    Core Setup (Root Window / Canvas Creation + Background Image on canvas)
    """
    # Root/Canvas Creation
    window = tk.Toplevel(root)
    window.geometry("1280x720")
    window.resizable(False, False)
    window.title(f"CampTrack / {leader_username} / Dashboard")

    canvas = tk.Canvas(window, width="1280", height="720", bg="white")
    canvas.pack(expand=True, fill="both")

    bg = tk.PhotoImage(file="Desert.png")
    canvas_bg = canvas.create_image(0, 0, image=bg, anchor="nw")
    canvas.tag_lower(canvas_bg)

    window.bg = bg


    """
    Leader and Camp Data Loading
    """
    CAMPS_FILE = "data/camps.csv"
    leaders = ScoutLeader.load_leaders("data/users.csv")
    selected_leader = leaders[leader_username]
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

            canvas.itemconfig(welcome, text="")
            canvas.after(300, show_widgets)

    slide_in()

    # Creating memory for Map and Notification Board slide-down widgets
    map_board = tk.PhotoImage(file="map_board.png")
    window.map_board = map_board
    canvas_map_board = canvas.create_image(960, -400, image=map_board)

    notif_msg_board = tk.PhotoImage(file="notif_msg_boards.png")
    window.notif_msg_board = notif_msg_board
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

    location_label = None

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

                    leader_text = str(row.get("leader", "") or "").strip()
                    leader_lower = leader_text.lower()

                    if leader_lower in ("", "na"):
                        if leader_lower != "unassigned":
                            row["leader"] = "unassigned"
                            changed = True
                        updated_rows.append(row)
                        continue

                    if leader_lower == "unassigned":
                        updated_rows.append(row)
                        continue

                    if end_dt + datetime.timedelta(days=1) < now:
                        row["leader"] = "unassigned"
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
                    leader_value = str(row.get("leader", "") or "").strip().lower()
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
        camps = []
        leader_username = selected_leader.username.strip().lower()

        try:
            with open(CAMPS_FILE, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    loc_value = str(row.get("location", "") or "").strip()
                    if loc_value != location:
                        continue

                    leader_value_raw = row.get("leader", "")
                    leader_value = str(leader_value_raw or "").strip()
                    leader_lower = leader_value.lower()

                    include_row = False
                    display_leader = leader_value

                    if leader_lower in ("", "na", "unassigned"):
                        include_row = True
                        display_leader = "unassigned"
                    elif leader_lower == leader_username:
                        include_row = True
                    else:
                        continue

                    try:
                        start_dt = datetime.datetime.strptime(row["start_date"], "%d/%m/%Y")
                        end_dt = datetime.datetime.strptime(row["end_date"], "%d/%m/%Y")
                    except (ValueError, TypeError):
                        continue

                    camp_obj = SimpleNamespace(
                        name=row["name"],
                        location=loc_value,
                        camp_type=row.get("camp_type", ""),
                        start_date=start_dt,
                        end_date=end_dt,
                        food_supply_per_day=int(row.get("food_supply_per_day", 0) or 0),
                        food_demand_per_day=int(row.get("food_demand_per_day", 0) or 0),
                        leader=display_leader,
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


    """Check if a camp is unassigned (no scout leader), extracts from the "leader" attribute of 
    the camp object created in camps_for_location(), meaning this function is used upon clicking on 
    individual camps (the treeview knows which camp is unsupervised from camps_for_location() - CSV "leader" lookup)."""
    def is_unassigned(camp):
        leader_value = getattr(camp, "leader", "")
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
        mapsubcanvas = tk.Canvas(mapsubframe, width='496', height='496', bg='light goldenrod')

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
                nonlocal location_label
                current_location = tent_icons.get(item)  # maybe don't use get, just use tent_icons[item]

                if location_label is not None:
                    location_label.destroy()

                location_label = tk.Label(
                    canvas,
                    text=f"{current_location}",
                    font=("Comic Sans MS", 30),
                    fg="white",
                    bg="#1095d6"
                )
                location_label.place(x=640, y=20, anchor="n")
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
        camps_treeview_subframe = tk.Frame(canvas, width=500, height=300, bg="light goldenrod")
        camps_treeview_window = canvas.create_window(320,525, window = camps_treeview_subframe, width=500, height=300)
        # Label for the camp treeview
        camps_listtitle = tk.Label(camps_treeview_subframe, text="Camps at this location:", font=("Comic Sans MS", 12), bg="light goldenrod", fg="black")
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
                            
                            # Ask for food requirement per camper
                            food_requirement_window = tk.Toplevel()
                            food_requirement_window.title("Set Food Requirement")
                            food_requirement_window.geometry("400x200")
                            food_requirement_window.configure(bg="lightblue")
                            
                            tk.Label(food_requirement_window, text=f"Food requirement per camper per day for {camp_name}:",
                                    bg="lightblue", font=("Comic Sans MS", 12), fg="black").pack(pady=10)
                            
                            food_entry = tk.Entry(food_requirement_window, font=("Comic Sans MS", 12), width=20)
                            food_entry.pack(pady=10)
                            food_entry.focus()
                            
                            def set_food_requirement():
                                try:
                                    food_req = float(food_entry.get())
                                    if food_req < 0:
                                        messagebox.showerror("Invalid input", "Food requirement must be non-negative")
                                        return
                                    elif food_req > 5:
                                        messagebox.showerror("Invalid input", "Food requirement must be 5 or less")
                                        return
                                    elif food_req != int(food_req):
                                        messagebox.showerror("Invalid input", "Food requirement must be a whole number")
                                        return
                                    
                                    food_req = int(food_req)
                                    food_result = selected_leader.set_food_requirement_per_camper(camp_name, food_req)
                                    if food_result.get("success"):
                                        messagebox.showinfo("Success", 
                                            f"Food requirement set!\n"
                                            f"Per camper: {food_req}\n"
                                            f"Total campers: {food_result.get('total_campers')}\n"
                                            f"Daily demand: {food_result.get('food_demand')}")
                                        food_requirement_window.destroy()
                                    else:
                                        messagebox.showerror("Error", "Failed to set food requirement")
                                except ValueError:
                                    messagebox.showerror("Invalid input", "Please enter a valid number")
                            
                            confirm_btn = tk.Button(food_requirement_window, text="Set Requirement",
                                                   command=set_food_requirement,
                                                   bg="white", fg="black", font=("Comic Sans MS", 12, "bold"),
                                                   activebackground="darkgreen")
                            confirm_btn.pack(pady=10)
                            
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
        createcampframe = tk.Frame(canvas, background="light goldenrod")
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
                                messagebox.showerror("Error", result.get("message", "Failed to assign camper"))
                                return

                        # Recalculate food demand after adding campers
                        food_result = selected_leader.recalculate_food_demand(camp_obj.name)
                        if food_result.get("success"):
                            messagebox.showinfo("Success", 
                                f"Added {len(selected_ids)} camper(s) to {camp_obj.name}\n"
                                f"Food demand updated: {food_result.get('food_demand')} units")
                        else:
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
                                messagebox.showerror("Error", result.get("message", "Failed to remove camper"))
                                return

                        # Recalculate food demand after removing campers
                        food_result = selected_leader.recalculate_food_demand(camp_obj.name)
                        if food_result.get("success"):
                            messagebox.showinfo("Success", 
                                f"Removed {len(selected_ids)} camper(s) from {camp_obj.name}\n"
                                f"Food demand updated: {food_result.get('food_demand')} units")
                        else:
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

                df = leaders[leader_username].get_campers_for_activity(camp_obj.name)
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
                    df_names = leaders[leader_username].get_camper_id_to_names(assigned_campers_list)

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
                                          bg="dodgerblue", fg="black", font=("Comic Sans MS", 14, "bold"))
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
                                       activebackground="darkgreen", activeforeground="black",
                                       relief="raised", bd=2)
                add_act_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew", ipady=5)

                remove_act_btn = tk.Button(button_frame, text="Remove Campers", command=open_remove_activity_window,
                                          bg="red", fg="black", font=("Comic Sans MS", 12, "bold"),
                                          activebackground="darkred", activeforeground="black",
                                          relief="raised", bd=2)
                remove_act_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew", ipady=5)

            def open_extra_notes_window(activity_name):
                extra_notes_window = tk.Toplevel()
                extra_notes_window.title(f"Extra notes for {activity_name}")
                extra_notes_window.geometry("600x600")

                extra_notes_window.configure(bg="lightblue")

                extra_notes_window.grid_columnconfigure(0, weight=1)
                extra_notes_window.grid_columnconfigure(1, weight=1)
                extra_notes_window.grid_rowconfigure(1, weight=1)

                extra_notes_window_title = tk.Label(extra_notes_window, text=f"Extra notes for {activity_name}",
                                                    bg="dodgerblue", font=("Comic Sans MS", 22))
                extra_notes_window_title.grid(row=0, column=0, columnspan=2, sticky='ew', padx=10, pady=(10, 5))

                # Get activity_id from activity_name and camp_name
                df_activities = pd.read_csv("data/activities.csv")
                activity_row = df_activities[(df_activities["camp_name"] == camp_obj.name) & 
                                            (df_activities["activity_name"] == activity_name)]
                
                if activity_row.empty:
                    error_label = tk.Label(extra_notes_window, text="Activity not found", bg="white", fg="black")
                    error_label.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
                    return
                
                activity_id = int(activity_row.iloc[0]["activity_id"])
                notes_str = activity_row.iloc[0]["extra_notes"]
                
                # Parse notes using pipe delimiter
                if pd.isna(notes_str) or str(notes_str).strip() == "" or str(notes_str).strip().lower() == "nan":
                    notes_list = []
                else:
                    notes_list = [n.strip() for n in str(notes_str).split("|") if n.strip()]

                # Display notes in a scrollable frame
                notes_frame = tk.Frame(extra_notes_window, bg="white", relief="sunken", bd=1)
                notes_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
                extra_notes_window.grid_rowconfigure(1, weight=1)

                if not notes_list:
                    no_notes_label = tk.Label(notes_frame, text="No notes yet", bg="white", fg="black", 
                                             font=("Comic Sans MS", 12))
                    no_notes_label.pack(pady=20)
                else:
                    # Scrollbar and listbox for notes
                    scrollbar = ttk.Scrollbar(notes_frame)
                    scrollbar.pack(side="right", fill="y")

                    notes_listbox = tk.Listbox(notes_frame, font=("Comic Sans MS", 11), 
                                              yscrollcommand=scrollbar.set, bg="white", fg="black",
                                              relief="flat", bd=0, activestyle="none", height=10)
                    scrollbar.config(command=notes_listbox.yview)
                    
                    for i, note in enumerate(notes_list):
                        notes_listbox.insert(i, f"• {note}")
                    
                    notes_listbox.pack(fill="both", expand=True)

                def add_extra_notes():
                    add_extra_notes_window = tk.Toplevel()
                    add_extra_notes_window.title(f"Add Extra notes for {activity_name}")
                    add_extra_notes_window.geometry("400x200")
                    add_extra_notes_window.configure(bg="lightblue")

                    add_extra_notes_window.grid_columnconfigure(0, weight=1)
                    add_extra_notes_window.grid_rowconfigure(1, weight=1)

                    add_notes_label = tk.Label(add_extra_notes_window, text="Enter new note:", bg="dodgerblue",
                                               font=("Comic Sans MS", 14, "bold"), fg="white")
                    add_notes_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

                    add_notes_entry = tk.Text(add_extra_notes_window, width=40, height=4, font=("Arial", 11), wrap="word")
                    add_notes_entry.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))

                    def save_notes(event=None):
                        new_notes = add_notes_entry.get("1.0", "end-1c").strip()
                        if not new_notes:
                            messagebox.showwarning("Empty Note", "Please enter some text before saving.")
                            return
                        try:
                            leaders[leader_username].add_activity_outcomes(activity_id, new_notes)
                            messagebox.showinfo("Success", "Note added successfully!")
                            add_extra_notes_window.destroy()
                            extra_notes_window.destroy()
                            open_extra_notes_window(activity_name)
                        except Exception as e:
                            messagebox.showerror("Error", f"Failed to add note: {str(e)}")

                    confirm_button = tk.Button(add_extra_notes_window, text="Add Note", command=save_notes, 
                                               bg="white", fg="black", font=("Comic Sans MS", 12, "bold"),
                                               padx=15, pady=8)
                    confirm_button.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))

                def remove_extra_notes():
                    remove_extra_notes_window = tk.Toplevel()
                    remove_extra_notes_window.title(f"Remove Extra notes for {activity_name}")
                    remove_extra_notes_window.geometry("400x400")
                    remove_extra_notes_window.configure(bg="lightblue")

                    remove_extra_notes_window.grid_columnconfigure(0, weight=1)
                    remove_extra_notes_window.grid_rowconfigure(2, weight=1)

                    remove_notes_label = tk.Label(remove_extra_notes_window, text="Select notes to remove:",
                                                  bg="white", font=("Comic Sans MS", 14, "bold"), fg="black")
                    remove_notes_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

                    if not notes_list:
                        no_notes_label = tk.Label(remove_extra_notes_window, text="No notes to remove",
                                                 bg="white", fg="black", font=("Comic Sans MS", 12))
                        no_notes_label.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
                    else:
                        # Checkbox-style selection like add/remove campers
                        tree_frame = tk.Frame(remove_extra_notes_window, bg="white")
                        tree_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

                        scrollbar = ttk.Scrollbar(tree_frame)
                        scrollbar.pack(side="right", fill="y")

                        notes_tree = ttk.Treeview(tree_frame, columns=("Note",), show="tree", 
                                                 yscrollcommand=scrollbar.set, height=10)
                        scrollbar.config(command=notes_tree.yview)

                        notes_tree.heading("#0", text="✓")
                        notes_tree.heading("Note", text="Note Content")
                        notes_tree.column("#0", width=30)
                        notes_tree.column("Note", width=350)

                        # Dictionary to track checkbox states
                        selected_notes = {}
                        
                        # Insert notes as rows
                        for i, note in enumerate(notes_list):
                            note_id = str(i)
                            selected_notes[note_id] = False
                            notes_tree.insert("", "end", note_id, text="☐", values=(note,))

                        # Click to toggle checkbox
                        def on_tree_click(event):
                            item = notes_tree.identify_row(event.y)
                            if not item:
                                return
                            col = notes_tree.identify_column(event.x)
                            if col == "#0":
                                current_state = selected_notes[item]
                                selected_notes[item] = not current_state
                                new_text = "☑" if not current_state else "☐"
                                notes_tree.item(item, text=new_text)

                        notes_tree.bind("<Button-1>", on_tree_click)
                        notes_tree.pack(fill="both", expand=True)

                        # Button frame
                        button_frame = tk.Frame(remove_extra_notes_window, bg="lightblue")
                        button_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
                        button_frame.grid_columnconfigure(0, weight=1)
                        button_frame.grid_columnconfigure(1, weight=1)

                        def select_all():
                            for note_id in selected_notes:
                                selected_notes[note_id] = True
                            for item in notes_tree.get_children():
                                notes_tree.item(item, text="☑")

                        def deselect_all():
                            for note_id in selected_notes:
                                selected_notes[note_id] = False
                            for item in notes_tree.get_children():
                                notes_tree.item(item, text="☐")

                        ttk.Button(button_frame, text="Select All", command=select_all).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
                        ttk.Button(button_frame, text="Deselect All", command=deselect_all).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

                        def confirm_remove():
                            selected_indices = [int(note_id) for note_id, selected in selected_notes.items() if selected]
                            if not selected_indices:
                                messagebox.showwarning("No selection", "Please select at least one note to remove.")
                                return

                            try:
                                for idx in sorted(selected_indices, reverse=True):
                                    note_to_remove = notes_list[idx]
                                    result = leaders[leader_username].remove_activity_outcomes(activity_id, note_to_remove)
                                    if not result:
                                        messagebox.showerror("Error", f"Failed to remove note: {note_to_remove}")
                                        return

                                messagebox.showinfo("Success", f"Removed {len(selected_indices)} note(s) successfully!")
                                remove_extra_notes_window.destroy()
                                extra_notes_window.destroy()
                                open_extra_notes_window(activity_name)
                            except Exception as e:
                                messagebox.showerror("Error", f"Failed to remove notes: {str(e)}")

                        confirm_btn = tk.Button(button_frame, text="Remove Selected Notes", command=confirm_remove,
                                               bg="white", fg="black", font=("Comic Sans MS", 12, "bold"),
                                               activebackground="darkred", activeforeground="white",
                                               relief="raised", bd=2, padx=10, pady=8)
                        confirm_btn.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=10, ipady=5)

                add_notes_button = tk.Button(extra_notes_window, text="Add Notes", command=add_extra_notes, 
                                             bg="white", fg="black", font=("Comic Sans MS", 14, "bold"),
                                             padx=15, pady=8)
                add_notes_button.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))

                remove_notes_button = tk.Button(extra_notes_window, text="Remove Notes", command=remove_extra_notes,
                                                bg="white", fg="black", font=("Comic Sans MS", 14, "bold"),
                                                padx=15, pady=8)
                remove_notes_button.grid(row=2, column=1, sticky="ew", padx=10, pady=(5, 10))

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

            remove_campers_button = tk.Button(makecampframe, text="View and Remove Campers",
                                              command=open_remove_campers_window, bg="white",
                                              font=("Comic Sans MS", 18))
            remove_campers_button.grid(row=8, column=1, columnspan=2, sticky="ew", padx=10, pady=(5, 10))

        # Generating tent icons on the map based on leader's camps
        positions = leaders[leader_username].create_leader_dict(camp_dict, location_coords)

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
        msgsubframe = tk.Frame(canvas, width=500, height=300, bg="light goldenrod")
        global msg_window
        msg_window = canvas.create_window(320,525, window = msgsubframe)
        try:
            from msg_system import MessagingApp
            MessagingApp(msgsubframe, leader_username)
        except Exception as e:
            error_label = tk.Label(msgsubframe, text="Messaging unavailable", font=("Comic Sans MS", 14), bg="white")
            error_label.grid(row=0, column=0, padx=10, pady=10)
            print("Failed to load MessagingApp:", e)

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
            location_label.destroy()
            root.update_idletasks()

        """Button Frame/window + Button Creation"""
        global ntfsubframe
        ntfsubframe = tk.Frame(canvas, width=520, height=140, bg="light goldenrod")
        ntfsubframe.grid_columnconfigure(0, weight=1)
        ntfsubframe.grid_columnconfigure(1, weight=1)
        ntfsubframe.grid_rowconfigure(0, weight=1)
        ntfsubframe.pack_propagate(False)
        # Styles for buttons
        style = ttk.Style()
        style.configure("Board.TButton", font=("Comic Sans MS", 16, "bold"), padding=(20, 20))
        # Button for going back to dashboard
        back_btn = tk.Button(ntfsubframe, text="Back to Dashboard",
                        command=show_main_dashboard,
                        bg="#FFFFFF", fg="black",
                        font=("Comic Sans MS", 14, "bold"),
                        activebackground="#FFFFFF", activeforeground="black",
                        relief="raised", bd=3,
                        padx=15, pady=15,
                        cursor="hand2")
        back_btn.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
    
    # Add hover effects for back button
        def on_enter_back(event):
            back_btn.config(bg="#1B5E20", relief="sunken", bd=4)
    
        def on_leave_back(event):
            back_btn.config(bg="#2E7D32", relief="raised", bd=3)
    
        back_btn.bind("<Enter>", on_enter_back)
        back_btn.bind("<Leave>", on_leave_back)

        """statistics window function"""
        def open_statistics_window():
            stats_window = tk.Toplevel()
            stats_window.title(f"Statistics - {selected_leader.username}")
            stats_window.geometry("450x600")
            stats_window.configure(bg="white")

            stats_window.grid_columnconfigure(0, weight=1)
            stats_window.grid_rowconfigure(1, weight=1)

            # Header with title and username
            header_frame = tk.Frame(stats_window, bg="#1095d6", height=60)
            header_frame.grid(row=0, column=0, sticky="ew")
            header_frame.pack_propagate(False)
            
            tk.Label(header_frame, text=f"📊 Statistics - {selected_leader.username}",
                    bg="#1095d6", font=("Comic Sans MS", 18, "bold"), fg="black").pack(anchor="w", padx=20, pady=10)

            """Get statistics"""
            stats_data = selected_leader.get_leader_statistics()

            if not stats_data.get("success"):
                no_stats_label = tk.Label(stats_window, text="No camps assigned yet",
                                        bg="white", fg="black", font=("Comic Sans MS", 14))
                no_stats_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=50)
                return

            # Canvas and scrollbar setup
            canvas_frame = tk.Canvas(stats_window, bg="white", highlightthickness=0)
            scrollbar = ttk.Scrollbar(stats_window, orient="vertical", command=canvas_frame.yview)
            scrollable_frame = tk.Frame(canvas_frame, bg="white")

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas_frame.configure(scrollregion=canvas_frame.bbox("all"))
            )

            canvas_frame.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas_frame.configure(yscrollcommand=scrollbar.set)

            canvas_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
            scrollbar.grid(row=1, column=1, sticky="ns", padx=0, pady=0)
            stats_window.grid_rowconfigure(1, weight=1)

            # Overall stats - compact card style
            overall = stats_data.get("overall", {})
            overall_frame = tk.Frame(scrollable_frame, bg="#E8F4F8", relief="flat", bd=0)
            overall_frame.pack(fill="x", padx=10, pady=(15, 10), ipady=10)

            title_label = tk.Label(overall_frame, text="📈 Overall Statistics",
                                bg="#E8F4F8", font=("Comic Sans MS", 14, "bold"), fg="black")
            title_label.pack(anchor="w", padx=10, pady=(5, 10))

            # Create a grid for overall stats (2 columns)
            stats_grid = tk.Frame(overall_frame, bg="#E8F4F8")
            stats_grid.pack(fill="x", padx=10, pady=5)

            overall_items = [
                (f"🏕️  Total Camps", str(overall.get('total_camps', 0))),
                (f"👥 Total Campers", str(overall.get('total_campers', 0))),
                (f"🎯 Total Activities", str(overall.get('total_activities', 0))),
                (f"📊 Activity Usage", f"{overall.get('activity_utilisation_rate', 0)}%"),
                (f"💰 Total Pay", f"{overall.get('total_pay', 0)} دج"),
                (f"🥘 Food Surplus", f"{overall.get('food_surplus', 0)} units"),
            ]

            for idx, (label, value) in enumerate(overall_items):
                row = idx // 2
                col = idx % 2
                
                stat_box = tk.Frame(stats_grid, bg="white", relief="raised", bd=1)
                stat_box.grid(row=row, column=col, padx=5, pady=5, sticky="ew", ipady=8)
                stats_grid.grid_columnconfigure(col, weight=1)
                
                tk.Label(stat_box, text=label, bg="white", font=("Comic Sans MS", 10, "bold"), fg="black").pack(anchor="w", padx=10, pady=(5, 2))
                tk.Label(stat_box, text=value, bg="white", font=("Comic Sans MS", 12, "bold"), fg="black").pack(anchor="w", padx=10, pady=(0, 5))

            # Per-camp stats
            camps = stats_data.get("camps", [])
            
            if camps:
                camps_title = tk.Label(scrollable_frame, text="📍 Camp Details",
                                    bg="white", font=("Comic Sans MS", 14, "bold"), fg="black")
                camps_title.pack(anchor="w", padx=15, pady=(20, 10))

            for camp in camps:
                camp_frame = tk.Frame(scrollable_frame, bg="#F5F5F5", relief="raised", bd=1)
                camp_frame.pack(fill="x", padx=10, pady=8, ipady=10)

                # Camp name header
                camp_header = tk.Frame(camp_frame, bg="#0D7FA8")
                camp_header.pack(fill="x", padx=0, pady=0)
                
                tk.Label(camp_header, text=f"  {camp['camp_name']} • {camp['location']}",
                        bg="#0D7FA8", font=("Comic Sans MS", 12, "bold"), fg="black").pack(anchor="w", pady=8)

                # Camp info in grid (2 columns)
                info_frame = tk.Frame(camp_frame, bg="#F5F5F5")
                info_frame.pack(fill="x", padx=15, pady=10)

                camp_info = [
                    (f"📅 Duration", camp['duration']),
                    (f"👥 Campers", str(camp['campers_at_camp'])),
                    (f"🎯 Activities", f"{camp['activities']['total_filled']}/{camp['activities']['total_capacity']} ({camp['activities']['utilisation_rate']}%)"),
                    (f"🥘 Food", f"Supply: {camp['food']['daily_supply']} | Demand: {camp['food']['daily_demand']} | Surplus: {camp['food']['daily_surplus']:+d}"),
                    (f"💰 Pay", f"{camp['pay']} دج"),
                ]

                for idx, (label, value) in enumerate(camp_info):
                    info_box = tk.Frame(info_frame, bg="white", relief="flat", bd=0)
                    info_box.pack(fill="x", pady=4, ipady=5)
                    
                    tk.Label(info_box, text=label, bg="white", font=("Comic Sans MS", 9, "bold"), fg="black", width=20, anchor="w").pack(side="left", padx=5)
                    tk.Label(info_box, text=value, bg="white", font=("Comic Sans MS", 9), fg="black", anchor="w").pack(side="left", fill="x", expand=True, padx=5)

                # Comments section (if exists)
                if camp.get("additional_comments"):
                    comments_frame = tk.Frame(camp_frame, bg="#FFF9E6", relief="flat", bd=0)
                    comments_frame.pack(fill="x", padx=15, pady=(10, 0), ipady=8)
                    
                    tk.Label(comments_frame, text="💬 Notes",
                            bg="#FFF9E6", font=("Comic Sans MS", 9, "bold"), fg="black").pack(anchor="w", padx=5, pady=(3, 5))
                    
                    for comment in camp["additional_comments"]:
                        tk.Label(comments_frame, text=f"• {comment}",
                                bg="#FFF9E6", font=("Comic Sans MS", 8), fg="black", wraplength=500, justify="left").pack(anchor="w", padx=15, pady=2)
        stats_btn = tk.Button(ntfsubframe, text="View Statistics",
                         command=open_statistics_window,
                         bg="#FFFFFF", fg="black",
                         font=("Comic Sans MS", 14, "bold"),
                         activebackground="#FFFFFF", activeforeground="black",
                         relief="raised", bd=3,
                         padx=15, pady=15,
                         cursor="hand2")
        stats_btn.grid(row=0, column=1, sticky="nsew", padx=12, pady=12)
    
    # Add hover effects for stats button
        def on_enter_stats(event):
            stats_btn.config(bg="#0D47A1", relief="sunken", bd=4)
    
        def on_leave_stats(event):
            stats_btn.config(bg="#1565C0", relief="raised", bd=3)
    
        stats_btn.bind("<Enter>", on_enter_stats)
        stats_btn.bind("<Leave>", on_leave_stats)

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
        tk.Label(header, text=leader_username, font=("Comic Sans MS", 18), background='#1095d6', fg="black").grid(row=0, column=0,
                                                                                              sticky='w', padx=10,
                                                                                              pady=10)
        def confirm_logout():
            if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
                window.destroy()
                root.deiconify()

        logout_btn = ttk.Button(header, text="Logout", command=confirm_logout)
        logout_btn.grid(row=0, column=1, sticky='e', padx=10, pady=10)