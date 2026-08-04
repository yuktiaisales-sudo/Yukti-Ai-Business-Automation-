class Automation:

    def __init__(
        self,
        name,
        status,
        last_run,
        records,
        success,
        failed,
        duration,
        machine,
        version
    ):

        self.name = name
        self.status = status
        self.last_run = last_run
        self.records = records
        self.success = success
        self.failed = failed
        self.duration = duration
        self.machine = machine
        self.version = version