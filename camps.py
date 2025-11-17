import csv


class Camp:
    def __init__(self, camp):
        self.camp = camp

    def load_camps_csv(self, path):
        with open(path) as f:
            reader = csv.DictReader(f)