from Users import ScoutLeader
from allocations import AllocationService

if __name__ == "__main__":
    leader = ScoutLeader("leader1")
    service = AllocationService()

    service.assign_camp_to_leader(leader.username, "campA")
    service.assign_camp_to_leader(leader.username, "campB")

    service.remove_camp_from_leader(leader.username, "campA")

    print("Camps assigned to", leader.username, ":", service.get_camps_for_leader(leader.username))