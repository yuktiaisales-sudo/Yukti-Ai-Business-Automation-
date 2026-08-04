from datetime import datetime


class AutomationEngine:

    def __init__(self):

        self.modules = {}

    # --------------------------
    # Register Module
    # --------------------------

    def register(self, name):

        self.modules[name] = {

            "name": name,

            "status": "Stopped",

            "last_run": "-",

            "records": 0,

            "success": 0,

            "failed": 0,

            "duration": "0 sec",

            "version": "1.0",

            "health": 100,

            "machine": "SERVER",

            "enabled": True
        }

     # -------------------------
    # NEW METHODS
    # -------------------------

    def start(self, name):
        if name in self.modules:
            self.modules[name]["status"] = "Running"
            self.modules[name]["last_run"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    def stop(self, name):
        if name in self.modules:
            self.modules[name]["status"] = "Idle"

    def error(self, name):
        if name in self.modules:
            self.modules[name]["status"] = "Error"

    def update_stats(self, name, records=0, success=0, failed=0, duration="0 sec"):
        if name in self.modules:
            self.modules[name]["records"] = records
            self.modules[name]["success"] = success
            self.modules[name]["failed"] = failed
            self.modules[name]["duration"] = duration

        self.modules[name]["last_run"] = datetime.now().strftime("%H:%M:%S")

    # --------------------------

    def get_module(self, name):

        return self.modules.get(name)

    # --------------------------

    def get_all(self):

        return self.modules

    # --------------------------

    def enable(self, name):

        self.modules[name]["enabled"] = True

    # --------------------------

    def disable(self, name):

        self.modules[name]["enabled"] = False