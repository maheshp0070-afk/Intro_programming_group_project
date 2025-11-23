import pandas as pd
import datetime


class Camp:

    def __init__(self, name, location, type, start_date, end_date, food_supply_per_day, food_demand_per_day, scout_leader,
                 pay):
        self.name = name
        self.location = location
        self.type = type
        self.start_date = start_date
        self.end_date = end_date
        self.food_supply_per_day = food_supply_per_day
        self.food_demand_per_day = food_demand_per_day
        self.scout_leader = scout_leader
        self.pay = pay

    @classmethod
    def load_camps(cls, file):
        df_camps = pd.read_csv(file)
        camps = {}

        for index, row in df_camps.iterrows():
            camp = Camp(
                name=row['name'],
                location=row['location'],
                type=row['type'],
                start_date=datetime.datetime.strptime(row['start_date'], '%d/%m/%Y'),
                end_date=datetime.datetime.strptime(row['end_date'], '%d/%m/%Y'),
                food_supply_per_day=int(row['food_supply_per_day']),
                food_demand_per_day=int(row['food_demand_per_day']),
                scout_leader=row['scout_leader'],
                pay=round(float(row['pay']), 2)
            )

            camps[camp.name] = camp

        return camps

    def get_campers(self, campers_file):
        df_campers = pd.read_csv(campers_file)

        campers = [row['camper_id'] for index, row in df_campers.iterrows() if type(row['camps']) == str if
                   self.name in row['camps'].split(',')]

        return campers


class User:

    def __init__(self, username, password, role, status):

        self.username = username
        self.password = password
        self.role = role
        self.status = status

    @classmethod
    def load_users(cls, file):

        df_users = pd.read_csv(file)
        users = {}

        for index, row in df_users.iterrows():
            user = User(
                username=row["username"],
                password=row["password"],
                role=row["role"],
                status=row["status"]
            )

            users[user.username] = user

        return users

    def get_camps(self, camps_dict):

        if self.role == "leader":
            camps = [camp for camp in camps_dict if camp.leader == self.username]
            return camps

    def create_camp(self, camps_dict, name, location, type, start_date, end_date, food_supply_per_day, leader, pay):

        if self.role == "coordinator":
            new_camp = Camp(
                name=name,
                location=location,
                type=type,
                start_date=datetime.datetime.strptime(start_date, '%d-%m-%Y'),  # needs changing depending on tkinter
                end_date=datetime.datetime.strptime(end_date, '%d-%m-%Y'),
                food_supply_per_day=int(food_supply_per_day),
                food_demand_per_day=0,
                leader=leader,
                pay=round(float(pay), 2)
            )

            camps_dict[new_camp.name] = new_camp

    def topup(self, camp, amount):

        if self.role == "coordinator":
            camp.food_supply_per_day += amount

    def update_pay(self, camp, new_pay):

        if self.role == "coordinator":
            camp.pay = round(float(new_pay), 2)

camps = Camp.load_camps("data/camps.csv")

print(camps["firstcamp"].type)








