import pandas as pd
from pdframe import Camp, User
import os


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
        df_activities = pd.read_csv("data/activities.csv")

        if camper_id not in df_campers.index:
            raise ValueError(f"Camper {camper_id} does not exist")

        camper = df_campers.loc[camper_id]

        assigned_activities = []
        for _, activity_row in df_activities.iterrows():
            assigned_campers = activity_row["assigned_campers"]
            if pd.notna(assigned_campers) and str(assigned_campers).strip():
                camper_ids = [int(c.strip()) for c in str(assigned_campers).split(",")]
                if camper_id in camper_ids:
                    assigned_activities.append({
                        "activity_id": activity_row["activity_id"],
                        "activity_name": activity_row["activity_name"],
                        "date": activity_row["date"],
                        "time": f"{activity_row['start_time']} - {activity_row['end_time']}"
                    })

        return {
            "camper_id": camper_id,
            "first_name": camper["first_name"],
            "last_name": camper["last_name"],
            "age": camper["age"],
            "camps": camper["camps"],
            "food": camper["food"],
            "assigned_activities": assigned_activities
        }

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
            return {
                "success": True,
                "message": f"{self.username} has been assigned to {camp_name}",
                "camp_name": camp_name,
                "scout_leader": self.username
            }
        
        elif current == self.username:
            return {
                "success": False,
                "message": f"{self.username} is already assigned to {camp_name}",
                "camp_name": camp_name,
                "scout_leader": current
            }
        else:
            return {
                "success": False, 
                "message": f"Camp {camp_name} is already assigned to {current}",
                "camp_name": camp_name,
                "scout_leader": current
            }

    def deselect_camp(self, camp_name):
        """Removes a camp from the leader if they have already selected it"""
        df = pd.read_csv("data/camps.csv", index_col="name")

        if camp_name not in df.index:
            raise ValueError(f"Camp {camp_name} does not exist")

        if df.loc[camp_name, "scout_leader"] == self.username:
            df.loc[camp_name, "scout_leader"] = "Na"
            df.to_csv("data/camps.csv")
            return {
                "success": True,
                "message": f"{self.username} has been removed from {camp_name}",
                "camp_name": camp_name,
                "scout_leader": "Na"
            }
        else:
            return {
                "success": False,
                "message": f"{self.username} is not assigned to {camp_name}",
                "camp_name": camp_name,
                "scout_leader": df.loc[camp_name, "scout_leader"]
            }

    def assign_camper(self, camper_id, camp):
        """Assings campers to a given camp"""
        # Also needs to be replaced with a bulk assign feature
        # Will change to raise an error if camper is already assigned to a camp
        df_camp = pd.read_csv("data/camps.csv", index_col="name")
        df_campers = pd.read_csv("data/campers.csv", index_col="camper_id")

        if camper_id not in df_campers.index:
            raise ValueError(f"User {camper_id} does not exist")
        if camp not in df_camp.index:
            raise ValueError(f"Camp {camp} does not exist")
        
        current_camp = df_campers.loc[camper_id, "camps"]

        if pd.notna(current_camp) and str(current_camp).strip() not in ("", "Na"):
            return {
                "success": False, 
                "message": f"Camper {camper_id} is already assigned to camp {current_camp}",
                "camper_id": camper_id,
                "camp": current_camp
            }
        
        df_campers.loc[camper_id, "camps"] = camp
        df_campers.to_csv("data/campers.csv", index=True)
        
        return {
            "success": True,
            "message": f"Camper {camper_id} has been assigned to {camp}",
            "camper_id": camper_id,
            "camp": camp
        }

    def remove_camper(self, camper_id):
        """Removes camper from their assigned camp. Returns status message."""
        df_campers = pd.read_csv("data/campers.csv", index_col="camper_id")
        
        if camper_id not in df_campers.index:
            raise ValueError(f"Camper {camper_id} does not exist")
        
        current_camp = df_campers.loc[camper_id, "camps"]
        
        # Check if camper is assigned to a camp
        if pd.isna(current_camp) or str(current_camp).strip() in ("", "Na"):
            return {
                "success": False,
                "message": f"Camper {camper_id} is not assigned to any camp",
                "camper_id": camper_id,
                "camp": None
            }
        
        removed_camp = current_camp
        df_campers.loc[camper_id, "camps"] = "Na"
        df_campers.to_csv("data/campers.csv", index=True)
        
        return {
            "success": True,
            "message": f"Camper {camper_id} has been removed from {removed_camp}",
            "camper_id": camper_id,
            "camp": removed_camp
        }

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
        duplicate_campers = []
        valid_campers = []
        
        for camper_id in camper_ids:
            if camper_id in current_camper_list:
                duplicate_campers.append(camper_id)
            else:
                valid_campers.append(camper_id)

        # Check capacity
        current_count = len(current_camper_list)
        max_capacity = df_activities.loc[activity_id, "max_capacity"]
        
        if current_count + len(valid_campers) > max_capacity:
            return {
                "success": False,
                "message": f"Cannot assign campers: capacity exceeded. Max: {max_capacity}, Currently: {current_count}, Trying to add: {len(valid_campers)}",
                "activity_id": activity_id,
                "assigned_count": 0,
                "duplicate_campers": duplicate_campers,
                "valid_campers": valid_campers
            }
        
        if not valid_campers and duplicate_campers:
            return {
                "success": False,
                "message": f"All {len(duplicate_campers)} camper(s) already assigned to activity {activity_id}",
                "activity_id": activity_id,
                "assigned_count": 0,
                "duplicate_campers": duplicate_campers,
                "valid_campers": []
            }

        new_campers = ",".join(map(str, valid_campers))
        if pd.notna(current_assigned) and str(current_assigned).strip():
            df_activities.loc[activity_id, "assigned_campers"] = f"{current_assigned},{new_campers}"
        else:
            df_activities.loc[activity_id, "assigned_campers"] = new_campers

        df_activities.to_csv("data/activities.csv", index=True)

        for camper_id in valid_campers:
            if camper_id not in df_campers.index:
                raise ValueError(f"Camper {camper_id} does not exist")

            current_activities = df_campers.loc[camper_id, "activities"]
            if pd.isna(current_activities) or str(current_activities).strip() == "":
                df_campers.loc[camper_id, "activities"] = str(activity_id)
            else:
                df_campers.loc[camper_id, "activities"] = f"{current_activities},{activity_id}"

        df_campers.to_csv("data/campers.csv", index=True)

        return {
            "success": True,
            "message": f"Assigned {len(valid_campers)} camper(s) to activity {activity_id}",
            "activity_id": activity_id,
            "assigned_count": len(valid_campers),
            "assigned_campers": valid_campers,
            "duplicate_campers": duplicate_campers
        }

    def remove_campers_from_activity(self, activity_id, camper_ids):
        """Removes campers from an activity. Returns status with details."""
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
            return {
                "success": False,
                "message": f"No campers assigned to activity {activity_id}",
                "activity_id": activity_id,
                "removed_count": 0,
                "not_assigned": camper_ids
            }

        camper_list = [int(c.strip()) for c in str(current_assigned).split(",")]
        removed_campers = []
        not_assigned_campers = []

        for camper_id in camper_ids:
            if camper_id not in camper_list:
                not_assigned_campers.append(camper_id)
                continue

            camper_list.remove(camper_id)
            removed_campers.append(camper_id)

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

        if removed_campers:
            return {
                "success": True,
                "message": f"Removed {len(removed_campers)} camper(s) from activity {activity_id}",
                "activity_id": activity_id,
                "removed_count": len(removed_campers),
                "removed_campers": removed_campers,
                "not_assigned": not_assigned_campers
        }
        else:
            return {
                "success": False,
                "message": f"No campers were removed from activity {activity_id}",
                "activity_id": activity_id,
                "removed_count": 0,
                "removed_campers": [],
                "not_assigned": not_assigned_campers
            }


    def view_camp_schedule(self, camp_name):
        """Returns a list of activities scheduled for a camp"""
        df_activities = pd.read_csv("data/activities.csv")
        df_camps = pd.read_csv("data/camps.csv", index_col="name")

        # Verify leader supervises this camp
        if camp_name not in df_camps.index:
            raise ValueError(f"Camp {camp_name} does not exist")
        
        if df_camps.loc[camp_name, "scout_leader"] != self.username:
            raise PermissionError(f"{self.username} does not supervise {camp_name}")

        camp_activities = df_activities[df_activities["camp_name"] == camp_name].copy()

        if camp_activities.empty:
            return {
                "success": False,
                "message": f"No activities scheduled for {camp_name}",
                "camp_name": camp_name,
                "activities": []
            }

        schedule = []
        for _, activity in camp_activities.iterrows():
            assigned = activity["assigned_campers"]
            camper_count = len(str(assigned).split(",")) if pd.notna(assigned) and str(assigned).strip() else 0
            max_capacity = activity["max_capacity"]

            schedule.append({
                "activity_id": activity["activity_id"],
                "activity_name": activity["activity_name"],
                "date": activity["date"],
                "start_time": activity["start_time"],
                "end_time": activity["end_time"],
                "camper_count": camper_count,
                "max_capacity": max_capacity,
                "assigned_campers": assigned if pd.notna(assigned) and str(assigned).strip() else None,
                "utilization": (camper_count / max_capacity * 100) if max_capacity > 0 else 0
            })

        return {
            "success": True,
            "message": f"Retrieved schedule for {camp_name}",
            "camp_name": camp_name,
            "activities": schedule
        }

    def assign_food_to_camper(self, camper_id, food_number):
        """Assigns food to camper. Returns status message."""
        df_campers = pd.read_csv("data/campers.csv", index_col="camper_id", dtype={"food": "Int64"})
        
        if camper_id not in df_campers.index:
            raise ValueError(f"Camper {camper_id} does not exist")
        
        current_food = df_campers.loc[camper_id, "food"]
        
        if pd.isna(current_food) or current_food != food_number:
            df_campers.loc[camper_id, "food"] = food_number
            df_campers.to_csv("data/campers.csv", index=True)
            return {
                "success": True,
                "message": f"Camper {camper_id} assigned {food_number} units of food",
                "camper_id": camper_id,
                "food_assigned": food_number
            }
        else:
            return {
                "success": False,
                "message": f"Camper {camper_id} already assigned {food_number} units of food",
                "camper_id": camper_id,
                "food_assigned": food_number
            }

    def add_activity_outcomes(self, activity, notes):
        """Allows leader to add activity outcomes, incidents, or special achievements. Returns status message."""
        df_activities = pd.read_csv("data/activities.csv", index_col="activity_id", dtype={"extra_notes": str})
        
        if activity not in df_activities.index:
            raise ValueError(f"Activity {activity} does not exist")
        
        cell = df_activities.loc[activity, "extra_notes"]
        if pd.isna(cell):
            cell = ""
        
        cell = cell + notes
        df_activities.loc[activity, "extra_notes"] = cell
        df_activities.to_csv("data/activities.csv", index=True)
        
        return {
            "success": True,
            "message": f"Activity notes for activity {activity} has been updated",
            "activity_id": activity,
            "notes": cell
        }

    def remove_activity_outcomes(self, activity, notes):
        """Allows leader to remove activity outcomes. Returns status message."""
        df_activities = pd.read_csv("data/activities.csv", index_col="activity_id", dtype={"extra_notes": str})
        
        if activity not in df_activities.index:
            raise ValueError(f"Activity {activity} does not exist")
        
        cell = df_activities.loc[activity, "extra_notes"]
        if pd.isna(cell):
            cell = ""
        
        if cell.find(notes) == -1:
            return {
                "success": False,
                "message": f"'{notes}' was not found in activity {activity} notes",
                "activity_id": activity,
                "notes": cell
            }
        else:
            cell = cell.replace(notes, "")
            df_activities.loc[activity, "extra_notes"] = cell
            df_activities.to_csv("data/activities.csv", index=True)
            return {
                "success": True,
                "message": f"'{notes}' removed from activity {activity} notes",
                "activity_id": activity,
                "notes": cell
            }



leaders = ScoutLeader.load_leaders("data/users.csv")
print(leaders["leader1"].view_camper_details(1))

