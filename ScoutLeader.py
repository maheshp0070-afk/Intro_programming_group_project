import pandas as pd
from pdframe import Camp, User
import os

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

        current = df.loc[camp_name, "scout_leader"]
        # treat NaN, empty string, or literal "Na" as unassigned
        if pd.isna(current) or str(current).strip() in ("", "Na"):
            df.loc[camp_name, "scout_leader"] = self.username
            df.to_csv("data/camps.csv")
            print(f"{self.username} assigned to {camp_name}")
        elif current == self.username:
            print(f"{self.username} is already assigned to this camp!")
        else:
            print(f"Camp {camp_name} is already assigned to {current}")

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

    def bulk_assign_campers(self, camp_name, csv_path):
        """
        Bulk-assign campers from a CSV file to a given camp.
        The CSV file is expected to have at least columns:
        'camper_id', 'name', 'age', 'contact' (you can adapt to your actual schema).
        """

        #Check the camp exists
        df_camps = pd.read_csv("data/camps.csv", index_col="name")
        if camp_name not in df_camps.index:
            raise ValueError(f"Camp {camp_name} does not exist")
        
        #Check the leader supervises this camp
        if df_camps.loc[camp_name, "scout_leader"] != self.username:
            raise PermissionError(f"{self.username} does not supervise {camp_name}")

        #Load existing campers table (or create empty if file missing)
        campers_path = "data/campers.csv"
        if os.path.exists(campers_path):
            df_existing = pd.read_csv(campers_path, index_col="camper_id")
        else:
            df_existing = pd.DataFrame(columns=["camper_id", "first_name", "last_name", "age", "camps"])
            df_existing.set_index("camper_id", inplace=True)

        #Load new campers from the CSV to import
        df_new = pd.read_csv(csv_path)

        # Basic validation: ensure column exists
        required_cols = {"camper_id", "first_name"}
        if not required_cols.issubset(df_new.columns):
            raise ValueError(f"CSV must contain at least columns: {required_cols}")

        #Set the camp for all imported campers
        df_new["camps"] = camp_name

        #Set camper_id as index for merging
        df_new.set_index("camper_id", inplace=True)

        #Merge: update existing campers or add new ones
        # If a camper_id already exists, we update their row; if not, we add it.
        df_combined = df_existing.combine_first(df_new)  # keeps existing where present
        df_combined.update(df_new)  # but override with new camp assignment

        # 7. Save back to campers.csv
        df_combined.to_csv(campers_path)

        print(f"Bulk assigned {len(df_new)} campers to {camp_name} from {csv_path}")


def nl():
    print("\n")

#pd_users = User.load_users("data/users.csv")
#print("\n")
#leader1_obj = pd_users["leader1"]
#leader1 = ScoutLeader(leader1_obj.username, leader1_obj.password, status=leader1_obj.status)
#print("\n")
#leader2_obj = pd_users["leader2"]
#leader2 = ScoutLeader(leader2_obj.username, leader2_obj.password, status=leader2_obj.status)
#print(leader2.camp_data("secondcamp"))
#print(ScoutLeader.view_all_camps())
leaders = ScoutLeader.load_leaders("data/users.csv")
#print(leaders["leader1"].view_all_camps())
#print(leaders["leader1"].camp_data("firstcamp"))
#print(leaders)
#leaders = {}
#for username, leader_obj in pd_users.items():
#    if leader_obj.role == "leader":
#        leaders[username] = ScoutLeader(
#            leader_obj.username,
#            leader_obj.password,
#            status=leader_obj.status
#        )
#leaders["leader1"].remove_camper(4)
#leaders["leader1"].remove_camper(3)
#nl()
#print(leaders["leader2"].camp_data("secondcamp"))
#print(leaders[("leader2")].select_camp("secondcamp"))
#print(ScoutLeader.view_all_camps())

leaders["leader1"].select_camp("firstcamp")
leaders["leader1"].bulk_assign_campers("firstcamp", "data/campers.csv")


#leader1 = ScoutLeader()
#print(leader1.view_all_camps(leader1))