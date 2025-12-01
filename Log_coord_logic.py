import pandas as pd
import datetime

class Camp:

    def __init__(self, name, location, camp_type, start_date, end_date, food_supply_per_day, food_demand_per_day, leader, pay):

       self.name = name
       self.location = location
       self.camp_type = camp_type
       self.start_date = start_date
       self.end_date = end_date
       self.food_supply_per_day = food_supply_per_day
       self.food_demand_per_day = food_demand_per_day
       self.leader = leader
       self.pay = pay

    @classmethod
    def load_camps (cls, file):

       df_camps = pd.read_csv(file)
       global camps
       camps = {}

       for index, row in df_camps.iterrows():

           camp = Camp(
               name = row['name'],
               location = row['location'],
               camp_type = row['camp_type'],
               start_date = datetime.datetime.strptime(row['start_date'], '%d-%m-%Y'),
               end_date = datetime.datetime.strptime(row['end_date'], '%d-%m-%Y'),
               food_supply_per_day = int(row['food_supply_per_day']),
               food_demand_per_day = int(row['food_demand_per_day']),
               leader = row['leader'],
               pay = round(float(row['pay']), 2)
           )

           camps[camp.name] = camp

       return camps

    def get_campers(self, campers_file):

       df_campers = pd.read_csv(campers_file)

       campers = [row['camper_id'] for index, row in df_campers.iterrows() if isinstance(row['camps'], str) and self.name in row['camps'].split(',')]

       return campers

    def save_camps(file):

       camp_data = []

       for camp in camps.values():

           camp_data.append({
               'name': camp.name,
               'location': camp.location,
               'camp_type': camp.camp_type,
               'start_date': camp.start_date.strftime('%d-%m-%Y'),
               'end_date': camp.end_date.strftime('%d-%m-%Y'),
               'food_supply_per_day': camp.food_supply_per_day,
               'food_demand_per_day': camp.food_demand_per_day,
               'leader': camp.leader,
               'pay': round(float(camp.pay), 2)
           })

       df_camps = pd.DataFrame(camp_data)
       df_camps.to_csv(file, index=False)

class User:

    def __init__ (self, username, password, role, status):

        self.username = username
        self.password = password
        self.role = role
        self.status = status

    @classmethod
    def load_users(cls, file):

        df_users = pd.read_csv(file)
        users = {}

        for index, row in df_users.iterrows():

            if row["role"] == cls.__name__.lower():
            
                user = cls(
                    username = row["username"],
                    password = row["password"],
                    status = row["status"]
                )
            
                users[user.username] = user
        
        return users
    
    @classmethod
    def load_all_users(cls, file):

        df_users = pd.read_csv(file)
        global all_users
        all_users = {}

        for index, row in df_users.iterrows():

            if row["role"] == 'admin':
                user = Admin(
                    username = row["username"],
                    password = row["password"],
                    status = row["status"]
                )
            elif row["role"] == 'coordinator':
                user = Coordinator(
                    username = row["username"],
                    password = row["password"],
                    status = row["status"]
                )
            elif row["role"] == 'leader':
                user = Leader(
                    username = row["username"],
                    password = row["password"],
                    status = row["status"]
                )
            
            all_users[user.username] = user
        
        return all_users

class Admin(User):

    def __init__(self, username, password, status):

        super().__init__(username, password, 'admin', status)

class Coordinator(User):

    def __init__(self, username, password, status):

        super().__init__(username, password, 'coordinator', status)

    def create_camp(self, camps_dict, name, location, camp_type, start_date, end_date, food_supply_per_day, pay):

        new_camp = Camp(
            name = name,
            location = location,
            camp_type = camp_type,
            start_date = start_date,
            end_date = end_date,
            food_supply_per_day = int(food_supply_per_day),
            food_demand_per_day = 0,
            leader = "unassigned",
            pay = round(float(pay), 2)
        )

        camps_dict[new_camp.name] = new_camp
    
    def set_food(self, camp, amount):
        
        camp.food_supply_per_day = amount

    def update_pay(self, camp, new_pay):

        camp.pay = round(float(new_pay), 2)
    
class Leader(User):

    def __init__(self, username, password, status):

        super().__init__(username, password, 'leader', status)

    def get_camps(self, camps_dict):

        camps = [camp for camp in camps_dict.values() if camp.leader == self.username]
        return camps

