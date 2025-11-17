class User:
    def __init__(self, username, role, enabled=True):
        self.username = username
        self.role = role   # "admin", "coordinator", "leader"
        self.enabled = enabled
        self.password = ""

class ScoutLeader(User):
    def __init__(self, username, enabled=True):
        super().__init__(username, role="leader", enabled=enabled)

        self.camps_supervised = []