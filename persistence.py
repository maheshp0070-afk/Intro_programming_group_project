import json
import os

DATA_DIR = "data"

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(path):
        return {}

    with open(path, "r") as f:
        return json.load(f)


def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)

    # ensure the folder exists
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)
