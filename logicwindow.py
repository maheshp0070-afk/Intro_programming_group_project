import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import datetime

root = tk.Tk()
root.geometry("500x500")
root.title("Irrelevant")
root.resizable(False, False)

makecampframe = tk.Frame(root, background="lightblue")
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
    camp_name_input = camp_name_entry.get()
    food_input = food_entry.get()
    pay_input = scout_payment.get()
    if (selected_syear == "Select a start year" or selected_smonth == "Select a start month" or selected_sday == "Select a start day" or selected_eyear == "Select an end year" or selected_emonth == "Select an end month" or selected_eday == "Select an end day"):
        tk.messagebox.showerror("Entry date error","Please enter dates in all the dropdown boxes")
        return None, None
    elif camp_name_input == "":
        tk.messagebox.showerror("Entry camp name error","Please enter a name for the camp")
        return None, None
    elif food_input == "":
        tk.messagebox.showerror("Entry food stock error","Please enter a whole number for food stock per day")
        return None, None
    elif pay_input == "":
        tk.messagebox.showerror("Entry payment error","Please enter a number for daily payment rate")
        return None, None
    else:
        selected_sdate = datetime.datetime(int(selected_syear), months.index(selected_smonth) + 1, int(selected_sday))
        selected_edate = datetime.datetime(int(selected_eyear), months.index(selected_emonth) + 1, int(selected_eday))

        if selected_sdate > selected_edate:
            tk.messagebox.showerror("Date error","Error!, camp end must be after start")
            return None, None
        elif selected_sdate < datetime.datetime.now() or selected_edate < datetime.datetime.now():
            tk.messagebox.showerror("Date error","Error!, camp must be set in the future")
            return None, None
        else:
            tk.messagebox.showinfo("Creation success", f"You have successfully created camp: {camp_name_input} on the selected dates: {selected_sdate.strftime('%Y-%m-%d')} to {selected_edate.strftime('%Y-%m-%d')} with {food_input} food stock per day {pay_input} and daily payment rate.") #location to be added, e.g. akfadou. Also to be formatted diff if day/overnight/expedition
            return selected_sdate, selected_edate

#Need to add text in the window as a user help/info, i.e. what day, overnight and exped means. Also need to dosomething similar for every window in app, like colour key for dashboard.


def get_years(): #check whether we can just use a list instead of function
    current_date = datetime.datetime.now()
    years = [str(current_date.year), str(current_date.year + 1)]
    return years


create_camp_label = tk.Label(Nameframe, text="Please enter camp name:", bg="lightblue", font=("Comic Sans MS", 10))
create_camp_label.grid(column = 0, row = 0, pady=5)
camp_name_entry = tk.Entry(Nameframe, width=30, validate = "key", validatecommand = (root.register(lambda x: len(x) < 25), '%P'))
camp_name_entry.grid(column = 1, row = 0, pady=5)

create_food_label = tk.Label(Nameframe, text="Food stock available per day:", bg="lightblue", font=("Comic Sans MS", 10))
create_food_label.grid(column = 0, row = 1, pady=5)
food_entry = tk.Entry(Nameframe, width=30, validate = "key", validatecommand=(root.register(lambda x: (x.isdigit() and int(x) <99 ) or x == ""), '%P'))
food_entry.grid(column = 1, row = 1 , pady=5)

payment_label = tk.Label(Nameframe, text="Daily payment rate for scout leader:", bg="lightblue", font=("Comic Sans MS", 10))
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

date_button = tk.Button(root, text="Create camp", command=button_select)
date_button.pack(pady=20)

root.mainloop()