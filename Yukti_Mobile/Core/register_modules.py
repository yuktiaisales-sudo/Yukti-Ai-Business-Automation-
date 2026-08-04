from .automation_engine import AutomationEngine


engine = AutomationEngine()




# ------------------------------
# Register Automation Modules
# ------------------------------

engine.register(
    name="Outlook Email Reader"
)

engine.register(
    name="Google Sheet Automation"
)

engine.register(
    name="Power BI Refresh"
)

engine.register(
    name="Email Summary"
)

engine.register(
    name="Scheduler"
)

engine.register(
    name="Excel Automation"
)