import pandas as pd
from pdframe import Camp, User
import os
import datetime


class ScoutLeader(User):
    pd_camps = Camp.load_camps("data/camps.csv")
    pd_users = User.load_users("data/users.csv")

    def __init__(self, username, password, status="status"):
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
                    status=leader_obj.status
                )
        return leaders

    def view_all_camps(self):
        """Prints out the entire camps file"""
        view_camps = pd.read_csv("data/camps.csv")
        return view_camps.to_string()

    def view_campers(self, camp_name=None):
        """Prints out the data a specific camper, or all campers if no camper is given"""
        df_campers = pd.read_csv("data/campers.csv", index_col="camper_id")
        if camp_name:
            campers_in_camp = df_campers[df_campers['camps'] == camp_name]
        else:
            campers_in_camp = df_campers
        return campers_in_camp.to_string()

    def view_camper_details(self, camper_id):
        """Prints information for each camper"""
        df_campers = pd.read_csv("data/campers.csv", index_col="camper_id")
        df_activities = pd.read_csv("data/activities.csv", index_col="activity_id")

        if camper_id not in df_campers.index:
            raise ValueError(f"Camper {camper_id} does not exist")

        camper = df_campers.loc[camper_id]
        print(f"\n--- Camper Details ---")
        print(f"ID: {camper_id}")
        print(f"Name: {camper['first_name']} {camper['last_name']}")
        print(f"Age: {camper['age']}")
        print(f"Camp: {camper['camps']}")

        assigned_activities = []
        for activity_id, activity_row in df_activities.iterrows():
            assigned_campers = activity_row["assigned_campers"]
            if pd.notna(assigned_campers) and str(assigned_campers).strip():
                camper_ids = [int(c.strip()) for c in str(assigned_campers).split(",")]
                if camper_id in camper_ids:
                    assigned_activities.append({
                        "activity_id": activity_id,
                        "activity_name": activity_row["activity_name"],
                        "date": activity_row["date"],
                        "time": f"{activity_row['start_time']} - {activity_row['end_time']}"
                    })

        if assigned_activities:
            print(f"\nAssigned Activities:")
            for activity in assigned_activities:
                print(
                    f"  - {activity['activity_name']} (ID: {activity['activity_id']}) on {activity['date']} at {activity['time']}")
        else:
            print(f"\nNo activities assigned")
        print()

    def camp_data(self, name):
        """Prints out the camp data only for the specific data"""
        view_camps = pd.read_csv("data/camps.csv", index_col="name")
        return view_camps.loc[name].to_string()

    def select_camp(self, camp_name):
        """Allows leaders to select a camp"""
        df = pd.read_csv("data/camps.csv", index_col="name")

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
        """Removes a camp from the leader if they have already selected it"""
        df = pd.read_csv("data/camps.csv", index_col="name")

        if camp_name not in df.index:
            raise ValueError(f"Camp {camp_name} does not exist")

        if df.loc[camp_name, "scout_leader"] == self.username:
            df.loc[camp_name, "scout_leader"] = "Na"
            df.to_csv("data/camps.csv")
            print(f"{self.username} has deselected {camp_name}")
        else:
            print(f"{self.username} does not supervise {camp_name}")

    def assign_camper(self, id, camp):
        """Assings campers to a given camp"""
        # Also needs to be replaced with a bulk assign feature
        # Will change to raise an error if camper is already assigned to a camp
        df_camp = pd.read_csv("data/camps.csv", index_col="name")
        df = pd.read_csv("data/campers.csv", index_col="camper_id")
        if id not in df.index:
            raise ValueError(f"User {id} does not exist")
        if camp not in df_camp.index:
            raise ValueError(f"Camp {camp} does not exist")

        else:
            df.loc[id, "camps"] = camp
            df.to_csv("data/campers.csv")
            print(f"User {id} assigned to {camp}")

    def remove_camper(self, id):
        """Removes camper from a given camp"""
        # Again might be reworked with assign_camper such that it works with bulk assignment
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

    def view_camp_activities(self, camp_name):
        """Shows activities for the given camp"""
        df = pd.read_csv("data/activities.csv")
        camp_activities = df[df['camp_name'] == camp_name]
        return camp_activities.to_string()

    def assign_campers_to_activity(self, activity_id, camper_ids):
        """Bulk assigns campers to a given activity"""
        # What is the argument for camper_ids? It shouldn't be a number as it needs to be iterable?
        # Use a similar code to bulk assign campers to camper
        df_activities = pd.read_csv("data/activities.csv", index_col="activity_id", dtype={"assigned_campers": str})
        df_campers = pd.read_csv("data/campers.csv", index_col="camper_id", dtype={"activities": str})

        if activity_id not in df_activities.index:
            raise ValueError(f"Activity {activity_id} does not exist")

        camp_name = df_activities.loc[activity_id, "camp_name"]
        df_camps = pd.read_csv("data/camps.csv", index_col="name")
        if df_camps.loc[camp_name, "scout_leader"] != self.username:
            raise PermissionError(f"You do not supervise camp {camp_name}")

        current_assigned = df_activities.loc[activity_id, "assigned_campers"]
        current_camper_list = [int(c.strip()) for c in str(current_assigned).split(",")] if pd.notna(
            current_assigned) and str(current_assigned).strip() else []

        # Check for duplicates
        for camper_id in camper_ids:
            if camper_id in current_camper_list:
                raise ValueError(f"Camper {camper_id} is already assigned to activity {activity_id}")

        current_count = len(current_camper_list)
        max_capacity = df_activities.loc[activity_id, "max_capacity"]
        if current_count + len(camper_ids) > max_capacity:
            raise ValueError(
                f"Cannot assign campers: capacity exceeded for activity {activity_id}. Max capacity is {max_capacity}, currently assigned {current_count}.")

        new_campers = ",".join(map(str, camper_ids))
        if pd.notna(current_assigned) and str(current_assigned).strip():
            df_activities.loc[activity_id, "assigned_campers"] = f"{current_assigned},{new_campers}"
        else:
            df_activities.loc[activity_id, "assigned_campers"] = new_campers

        df_activities.to_csv("data/activities.csv", index=True)

        for camper_id in camper_ids:
            if camper_id not in df_campers.index:
                raise ValueError(f"Camper {camper_id} does not exist")

            current_activities = df_campers.loc[camper_id, "activities"]
            if pd.isna(current_activities) or str(current_activities).strip() == "":
                df_campers.loc[camper_id, "activities"] = str(activity_id)
            else:
                df_campers.loc[camper_id, "activities"] = f"{current_activities},{activity_id}"

        df_campers.to_csv("data/campers.csv", index=True)
        print(f"Assigned {len(camper_ids)} campers to activity {activity_id}")

    def remove_campers_from_activity(self, activity_id, camper_ids):
        """Removes the camper from the assigned activity"""
        df_activities = pd.read_csv("data/activities.csv", index_col="activity_id", dtype={"assigned_campers": str})
        df_campers = pd.read_csv("data/campers.csv", index_col="camper_id", dtype={"activities": str})

        if activity_id not in df_activities.index:
            raise ValueError(f"Activity {activity_id} does not exist")

        camp_name = df_activities.loc[activity_id, "camp_name"]
        df_camps = pd.read_csv("data/camps.csv", index_col="name")
        if df_camps.loc[camp_name, "scout_leader"] != self.username:
            raise PermissionError(f"{self.username} does not supervise {camp_name}")

        current_assigned = df_activities.loc[activity_id, "assigned_campers"]
        if pd.isna(current_assigned) or str(current_assigned).strip() == "":
            print(f"No campers assigned to activity {activity_id}")
            return

        camper_list = [int(c.strip()) for c in str(current_assigned).split(",")]
        removed_count = 0

        for camper_id in camper_ids:
            if camper_id not in camper_list:
                print(f"Camper {camper_id} is not assigned to activity {activity_id}")
                continue

            camper_list.remove(camper_id)
            removed_count += 1

            if camper_id in df_campers.index:
                camper_activities = df_campers.loc[camper_id, "activities"]
                if pd.isna(camper_activities) or str(camper_activities).strip() == "":
                    continue
                activity_list = [int(a.strip()) for a in str(camper_activities).split(",")]
                if activity_id in activity_list:
                    activity_list.remove(activity_id)
                    if activity_list:
                        df_campers.loc[camper_id, "activities"] = ",".join(map(str, activity_list))
                    else:
                        df_campers.loc[camper_id, "activities"] = ""

        if camper_list:
            df_activities.loc[activity_id, "assigned_campers"] = ",".join(map(str, camper_list))
        else:
            df_activities.loc[activity_id, "assigned_campers"] = ""

        df_activities.to_csv("data/activities.csv", index=True)
        df_campers.to_csv("data/campers.csv", index=True)

        if removed_count > 0:
            print(f"Removed {removed_count} camper(s) from activity {activity_id}")

    def view_camp_schedule(self, camp_name):
        """shows a little timetable of activities for the camp"""
        # shall we change this to return an output rather than print it?
        df_activities = pd.read_csv("data/activities.csv")
        df_camps = pd.read_csv("data/camps.csv", index_col="name")

        # Verify leader supervises this camp
        if df_camps.loc[camp_name, "scout_leader"] != self.username:
            raise PermissionError(f"{self.username} does not supervise {camp_name}")

        camp_activities = df_activities[df_activities["camp_name"] == camp_name].copy()

        if camp_activities.empty:
            print(f"No activities scheduled for {camp_name}")
            return

        print(f"\n{'=' * 80}")
        print(f"ACTIVITY SCHEDULE FOR {camp_name.upper()}")
        print(f"{'=' * 80}\n")

        for _, activity in camp_activities.iterrows():
            assigned = activity["assigned_campers"]
            camper_count = len(str(assigned).split(",")) if pd.notna(assigned) and str(assigned).strip() else 0
            max_capacity = activity["max_capacity"]

            print(f"Activity ID: {activity['activity_id']} | {activity['activity_name']}")
            print(f"  Date: {activity['date']} | Time: {activity['start_time']} - {activity['end_time']}")
            print(f"  Capacity: {camper_count}/{max_capacity}")
            print(f"  Assigned Campers: {assigned if pd.notna(assigned) and str(assigned).strip() else 'None'}")
            print()

    def assign_food_to_camper(self, camper_id, food_number):
        """Assigns food to camper"""
        df_campers = pd.read_csv("data/campers.csv", index_col="camper_id", dtype={"food": "Int64"})

        if camper_id not in df_campers.index:
            raise ValueError(f"Camper {camper_id} does not exist")

        current_food = df_campers.loc[camper_id, "food"]

        """Check if current_food is NaN or not equal to food_number"""
        if pd.isna(current_food) or current_food != food_number:
            df_campers.loc[camper_id, "food"] = food_number
            df_campers.to_csv("data/campers.csv", index=True)
            print(f"Camper {camper_id} assigned {food_number} units of food")
        else:
            print(f"Camper {camper_id} already assigned {food_number} units of food")

    def add_activity_outcomes(self, activity, notes):
        """Allows leader to add in activity outcomes, incidents, or special achievements"""
        df_activities = pd.read_csv("data/activities.csv", index_col="activity_id", dtype={"extra_notes": str})
        cell = df_activities.loc[activity, "extra_notes"]
        if pd.isna(cell):
            cell = ""
        cell = cell + notes
        df_activities.loc[activity, "extra_notes"] = cell
        df_activities.to_csv("data/activities.csv")
        print(f"Activity notes for activity {activity} has been updated")

    def remove_activity_outcomes(self, activity, notes):
        """Allows leader to remove activity outcomes"""
        df_activities = pd.read_csv("data/activities.csv", index_col="activity_id", dtype={"extra_notes": str})
        cell = df_activities.loc[activity, "extra_notes"]
        if pd.isna(cell):
            cell = ""
        if cell.find(notes) == -1:
            raise ValueError(f"This was not in the activity notes for activity {activity}")
        else:
            cell = cell.replace(notes, "")
            df_activities.loc[activity, "extra_notes"] = cell
            df_activities.to_csv("data/activities.csv")
            print(f"{notes} removed from activity {activity} notes")

    def load_camps_for_leader(self, file):
        df_camps = pd.read_csv(file)
        camps = {}

        for index, row in df_camps.iterrows():
            if row["scout_leader"] == self.username:
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

    def create_leader_dict(self, dict, co_ords):
        leader_camps = {}
        for key, value in dict.items():
            if value.location in co_ords:
                leader_camps[value.location] = co_ords[value.location]
        return leader_camps

    def get_leader_statistics(self):
        """Returns statistics for all camps led by this scout leader"""
        df_camps = pd.read_csv("data/camps.csv", index_col="name")
        df_campers = pd.read_csv("data/campers.csv", index_col="camper_id")
        df_activities = pd.read_csv("data/activities.csv", index_col="activity_id", dtype={"assigned_campers": str})

        """Get all camps for this leader"""
        leader_camps = df_camps[df_camps["scout_leader"] == self.username]

        if leader_camps.empty:
            return {
                "success": False,
                "message": f"{self.username} has not been assigned to any camps",
                "leader": self.username,
                "camps": [],
                "overall": {}
            }

        camp_stats = []
        overall_stats = {
            "total_camps": 0,
            "total_campers": 0,
            "total_activities": 0,
            "total_activity_slots": 0,
            "total_activity_capacity": 0,
            "total_food_supply": 0,
            "total_food_demand": 0,
            "total_pay": 0
        }

        for camp_name, camp_data in leader_camps.iterrows():
            camp_campers = df_campers[df_campers["camps"] == camp_name]
            camp_activities = df_activities[df_activities["camp_name"] == camp_name]

            """Participation stats"""
            total_campers = len(camp_campers)
            assigned_campers = len(camp_campers[camp_campers["camps"] != "Na"])
            participation_rate = (assigned_campers / total_campers * 100) if total_campers > 0 else 0

            """Activity stats"""
            total_activities = len(camp_activities)
            total_activity_capacity = 0
            total_activity_slots_filled = 0

            for _, activity in camp_activities.iterrows():
                total_activity_capacity += activity["max_capacity"]
                assigned = activity["assigned_campers"]
                if pd.notna(assigned) and str(assigned).strip():
                    slot_count = len(str(assigned).split(","))
                    total_activity_slots_filled += slot_count

            activity_utilisation = (
                    total_activity_slots_filled / total_activity_capacity * 100) if total_activity_capacity > 0 else 0

            """Food resources"""
            total_food_supply = camp_data["food_supply_per_day"]
            total_food_demand = camp_data["food_demand_per_day"]
            food_surplus = total_food_supply - total_food_demand

            """Pay info"""
            camp_pay = camp_data["pay"]

            """Additional Comment"""
            additional_comments = []
            for _, activity in camp_activities.iterrows():
                notes = activity.get("extra_notes", "")
                if pd.notna(notes) and str(notes).strip():
                    additional_comments.append({
                        "activity_id": activity.name,
                        "activity_name": activity["activity_name"],
                        "comment": str(notes).strip()
                    })

            camp_stats.append({
                "camp_name": camp_name,
                "location": camp_data["location"],
                "camp_type": camp_data["type"],
                "duration": f"{camp_data['start_date']} to {camp_data['end_date']}",
                "participation": {
                    "total_campers": int(total_campers),
                    "assigned_campers": int(assigned_campers),
                    "participation_rate": round(participation_rate, 1)
                },
                "activities": {
                    "total_activities": int(total_activities),
                    "total_capacity": int(total_activity_capacity),
                    "total_filled": int(total_activity_slots_filled),
                    "utilisation_rate": round(activity_utilisation, 1)
                },
                "food": {
                    "daily_supply": int(total_food_supply),
                    "daily_demand": int(total_food_demand),
                    "daily_surplus": int(food_surplus)
                },
                "pay": int(camp_pay),
                "additional_comments": additional_comments
            })

            """ Update overall stats"""
            overall_stats["total_camps"] += 1
            overall_stats["total_campers"] += total_campers
            overall_stats["total_activities"] += total_activities
            overall_stats["total_activity_slots"] += total_activity_slots_filled
            overall_stats["total_activity_capacity"] += total_activity_capacity
            overall_stats["total_food_supply"] += total_food_supply
            overall_stats["total_food_demand"] += total_food_demand
            overall_stats["total_pay"] += camp_pay

        """Calculate overall rates"""
        overall_activity_utilisation = (
                overall_stats["total_activity_slots"] / overall_stats["total_activity_capacity"] * 100) if \
            overall_stats["total_activity_capacity"] > 0 else 0
        overall_food_surplus = overall_stats["total_food_supply"] - overall_stats["total_food_demand"]

        overall_stats["activity_utilisation_rate"] = round(overall_activity_utilisation, 1)
        overall_stats["food_surplus"] = overall_food_surplus

        return {
            "success": True,
            "leader": self.username,
            "camps": camp_stats,
            "overall": overall_stats
        }

# print(create_leader_dict(camp_dict))

# leaders = ScoutLeader.load_leaders("data/users.csv")
# camp_dict = leaders["leader1"].load_camps_for_leader("data/camps.csv")
# print(camp_dict)


# leaders = ScoutLeader.load_leaders("data/users.csv")
# print(leaders["leader1"].assign_food_to_camper(4, 20))
# print(leaders["leader2"].load_camps_for_leader("data/camps.csv"))

# for value in camp_dict.values():
#    print(value.location)