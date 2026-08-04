import json
from datetime import datetime

LOG_FILE = "../Logs/automation_log.json"


def log(module, status, message):

    try:

        with open(LOG_FILE, "r") as f:

            data = json.load(f)

    except:

        data = []

    data.append({

        "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),

        "module": module,

        "status": status,

        "message": message

    })

    with open(LOG_FILE, "w") as f:

        json.dump(data, f, indent=4)