import sqlite3
import os
from .automation_engine import AutomationEngine

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = AutomationEngine()
    return _engine

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "Database",
    "yukti.db"
)


DEFAULT_MODULES = [

    ("Outlook Email Reader", "Idle"),
    ("Excel Automation", "Idle"),
    ("Google Sheet Automation", "Idle"),
    ("Google Sheet Update", "Idle"),
    ("Power BI Refresh", "Idle"),
    ("Email Summary", "Idle"),
    ("Scheduler", "Idle")

]


def register_default_modules():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS automation_modules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        module_name TEXT,
        status TEXT,
        last_run TEXT,
        records INTEGER DEFAULT 0,
        success INTEGER DEFAULT 0,
        failed INTEGER DEFAULT 0,
        duration TEXT,
        version TEXT,
        machine TEXT,
        health INTEGER DEFAULT 100,
        enabled INTEGER DEFAULT 1
    )
    """)

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM automation_modules")

    count = cursor.fetchone()[0]

    if count == 0:

        for module, status in DEFAULT_MODULES:

            cursor.execute("""

            INSERT INTO automation_modules
            (
                module_name,
                status,
                last_run,
                records,
                success,
                failed,
                duration,
                version,
                machine,
                health,
                enabled
            )

            VALUES
            (
                ?, ?, '', 0, 0, 0, '', '2.0', '', 100, 1
            )

            """, (module, status))

    conn.commit()
    conn.close()