from persistence import load_json, save_json

ALLOCATIONS_FILE = 'allocations.json'

class AllocationService: 

    def __init__(self):
        self.allocations = load_json(ALLOCATIONS_FILE) or []

    def save(self):
        save_json(ALLOCATIONS_FILE, self.allocations)

    def get_camps_for_leader(self, leader_username):
        return [a["camp_id"] for a in self.allocations if a["leader"] == leader_username]

    def assign_camp_to_leader(self, leader_username, camp_id):
        for a in self.allocations:
            if a["leader"] == leader_username and a["camp_id"] == camp_id:
                return  # already assigned
        self.allocations.append({"leader": leader_username, "camp_id": camp_id})
        self.save()

    def remove_camp_from_leader(self, leader_username, camp_id):
        self.allocations = [
            a for a in self.allocations
            if not (a["leader"] == leader_username and a["camp_id"] == camp_id)
        ]
        self.save()
        