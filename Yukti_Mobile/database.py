import sqlite3
import os

# Database Location
DB_PATH = os.path.join(os.path.dirname(__file__), "yukti.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # ===================================================
    # USERS
    # ===================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE,

        password TEXT,

        role TEXT,

        department TEXT,

        email TEXT,

        last_login TEXT

    )
    """)

    # ===================================================
    # AUTOMATION MODULES
    # ===================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS automation_modules (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        module_name TEXT,

        status TEXT,

        last_run TEXT,

        records INTEGER,

        success INTEGER,

        failed INTEGER,

        duration TEXT,

        version TEXT,

        machine TEXT,

        health INTEGER,

        enabled INTEGER

    )
    """)

    # ===================================================
    # AUTOMATION LOGS
    # ===================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS automation_logs (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        log_datetime TEXT,

        module_name TEXT,

        status TEXT,

        message TEXT,

        records INTEGER,

        duration TEXT,

        username TEXT

    )
    """)

    # ===================================================
    # LEADS
    # ===================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,

        mobile TEXT,

        email TEXT,

        project TEXT,

        source TEXT,

        crm TEXT,

        status TEXT,

        created_date TEXT,

        uploaded_date TEXT

    )
    """)

    # ===================================================
    # PROJECTS
    # ===================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        project_name TEXT,

        crm_name TEXT,

        active INTEGER

    )
    """)

    # ===================================================
    # SETTINGS
    # ===================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        setting_name TEXT,

        setting_value TEXT

    )
    """)

    conn.commit()
    conn.close()

    print("✅ Yukti-AI Database Ready")


if __name__ == "__main__":
    create_tables()