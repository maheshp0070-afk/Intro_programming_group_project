import pandas as pd
from pdframe import Camp, User

class ScoutLeader(User):
    pd_camps = Camp.load_camps("data/camps.csv")
    pd_users = User.load_users("data/users.csv")
    def __init__(self, username, password, status="active"):
        super().__init__(username, password, role="leader", status=status)

    @classmethod
    def load_leaders(cls, file):
        """Creates objects for user such that every user can call their own instance functions like camp_data"""
        pd_users = User.load_users(file)
        leaders = {}
        for username, leader_obj in pd_users.items():
            if leader_obj.role == "leader":
                leaders[username] = ScoutLeader(
                    leader_obj.username,
                    leader_obj.password,
                    status=leader_obj.status)
        return leaders

    def view_all_camps(self):
        """Prints out the entire camps file"""
        view_camps = pd.read_csv("data/camps.csv")
        return view_camps.to_string()

    def camp_data(self, name):
        """Prints out the camp data only for the specific data"""
        view_camps = pd.read_csv("data/camps.csv", index_col = "name")
        return view_camps.loc[name].to_string()

    def select_camp(self, camp_name):
        """Allows leaders to select a camp"""
        df = pd.read_csv("data/camps.csv", index_col = "name")

        if camp_name not in df.index:
            raise ValueError(f"Camp {camp_name} does not exist")

        if df.loc[camp_name, "scout_leader"] == "Na":
            df.loc[camp_name, "scout_leader"] = self.username
            df.to_csv("data/camps.csv")
            print(f"{self.username} assigned to {camp_name}")
        else:
            print(f"{self.username} is already assigned to this camp!")

    def deselect_camp(self, camp_name):
        df = pd.read_csv("data/camps.csv", index_col = "name")

        if camp_name not in df.index:
            raise ValueError(f"Camp {camp_name} does not exist")

        if df.loc[camp_name, "scout_leader"] == self.username:
            df.loc[camp_name, "scout_leader"] = "Na"
            df.to_csv("data/camps.csv")
            print(f"{self.username} has deselected {camp_name}")
        else:
            print(f"{self.username} does not supervise {camp_name}")

    def assign_camper(self, id, camp):
        df_camp = pd.read_csv("data/camps.csv", index_col = "name")
        df = pd.read_csv("data/campers.csv", index_col = "camper_id")
        if id not in df.index:
            raise ValueError(f"User {id} does not exist")
        if camp not in df_camp.index:
            raise ValueError(f"Camp {camp} does not exist")

        else:
            df.loc[id, "camps"] = camp
            df.to_csv("data/campers.csv")
            print(f"User {id} assigned to {camp}")

    def remove_camper(self, id):
        df = pd.read_csv("data/campers.csv", index_col="camper_id")
        if id not in df.index:
            raise ValueError(f"User {id} does not exist")
        if df.loc[id, "camps"] == "Na":
            print(f"User {id} is not assigned to any camp")
        else:
            removed_camp = df.loc[id, "camps"]
            df.loc[id, "camps"] = "Na"
            df.to_csv("data/campers.csv")
            print(f"User {id} removed from {removed_camp}")


def nl():
    print("\n")

pd_users = User.load_users("data/users.csv")
print("\n")
#leader1_obj = pd_users["leader1"]
#leader1 = ScoutLeader(leader1_obj.username, leader1_obj.password, status=leader1_obj.status)
#print("\n")
#leader2_obj = pd_users["leader2"]
#leader2 = ScoutLeader(leader2_obj.username, leader2_obj.password, status=leader2_obj.status)
#print(leader2.camp_data("secondcamp"))
#print(ScoutLeader.view_all_camps())
leaders = ScoutLeader.load_leaders("data/users.csv")
print(leaders["leader1"].view_all_camps())
print(leaders["leader1"].camp_data("firstcamp"))
print(leaders)
#leaders = {}
#for username, leader_obj in pd_users.items():
#    if leader_obj.role == "leader":
#        leaders[username] = ScoutLeader(
#            leader_obj.username,
#            leader_obj.password,
#            status=leader_obj.status
#        )
leaders["leader1"].remove_camper(4)
#leaders["leader1"].remove_camper(3)
nl()
#print(leaders["leader2"].camp_data("secondcamp"))
#print(leaders[("leader2")].select_camp("secondcamp"))
#print(ScoutLeader.view_all_camps())






#leader1 = ScoutLeader()
#print(leader1.view_all_camps(leader1))