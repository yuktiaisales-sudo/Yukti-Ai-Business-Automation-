import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "Database",
    "yukti.db"
)

class UserModel:

    def get_all_users(self):

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row

        cur = conn.cursor()

        cur.execute("""
            SELECT
                project_name,
                user_name,
                active
            FROM project_users
            ORDER BY project_name,user_name
        """)

        rows = cur.fetchall()

        conn.close()

        return [dict(r) for r in rows]