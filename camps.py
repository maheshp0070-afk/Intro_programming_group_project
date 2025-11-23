from persistence import load_json, save_json

CAMPS_FILE = 'camps.json'
ALLOCATIONS_FILE = 'allocations.json'

class Camp:
    def __init__(self, camp_id, name, location, start_date, end_date, camp_type, food_units_per_day=0):
        self.camp_id = camp_id      
        self.name = name
        self.location = location
        self.start_date = start_date  
        self.end_date = end_date
        self.camp_type = camp_type    
        self.food_units_per_day = food_units_per_day

    def to_dict(self):
        return {
            "camp_id": self.camp_id,
            "name": self.name,
            "location": self.location,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "camp_type": self.camp_type,
            "food_units_per_day": self.food_units_per_day,
        }
    
    @staticmethod
    def from_dict(data):
        return Camp(
            camp_id=data["camp_id"],
            name=data["name"],
            location=data["location"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            camp_type=data["camp_type"],
            food_units_per_day=data.get("food_units_per_day", 0),
        )
    
def load_all_camps():
    data = load_json(CAMPS_FILE) or {}
    return {cid: Camp.from_dict(camp_dict) for cid, camp_dict in data.items()}

def save_all_camps(camps_dict):
    data = {cid: camp.to_dict() for cid, camp in camps_dict.items()}
    save_json(CAMPS_FILE, data)
