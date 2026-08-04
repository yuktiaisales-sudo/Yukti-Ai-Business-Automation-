import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "Database",
    "yukti.db"
)


class ProjectModel:

    def get_all_projects(self):

        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row

            cur = conn.cursor()

            print("Executing SQL...")

            cur.execute("""
            SELECT *
            FROM project_summary
            """)

            print("SQL Executed")

            rows = cur.fetchall()

            print("=" * 60)
            print("PROJECT SUMMARY")
            print(rows)
            print("=" * 60)

            conn.close()

            return [dict(r) for r in rows]

        except Exception as e:
            print("PROJECT ERROR:", e)
            return []