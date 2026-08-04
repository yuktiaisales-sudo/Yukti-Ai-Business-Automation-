import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "Database",
    "yukti.db"
)

DB_PATH = os.path.abspath(DB_PATH)


def update_module(
    module_name,
    status=None,
    records=None,
    success=None,
    failed=None,
    duration=None
):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    fields = []
    values = []

    if status is not None:
        fields.append("status=?")
        values.append(status)

        fields.append("last_run=?")
        values.append(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

    if records is not None:
        fields.append("records=?")
        values.append(records)

    if success is not None:
        fields.append("success=?")
        values.append(success)

    if failed is not None:
        fields.append("failed=?")
        values.append(failed)

    if duration is not None:
        fields.append("duration=?")
        values.append(duration)

    values.append(module_name)

    sql = f"""
        UPDATE automation_modules
        SET {", ".join(fields)}
        WHERE module_name=?
    """

    cur.execute(sql, values)

    print("=" * 60)
    print("Dashboard Logger")
    print("Database :", DB_PATH)
    print("Module   :", module_name)
    print("Rows Updated :", cur.rowcount)
    print("Records  :", records)
    print("=" * 60)

    conn.commit()
    conn.close()