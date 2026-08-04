import json
from datetime import datetime

LOG_FILE = "Yukti Mobile/Logs/automation_log.json"


def write_log(module, status, message):

    try:

        with open(LOG_FILE, "r") as file:
            data = json.load(file)

    except:
        data = []

    data.append({

        "time": datetime.now().strftime("%H:%M:%S"),

        "module": module,

        "status": status,

        "message": message

    })

    with open(LOG_FILE, "w") as file:
        json.dump(data, file, indent=4)