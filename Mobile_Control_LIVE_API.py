import sqlite3

from flask import Flask, render_template, request, redirect, session, url_for
import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from flask import request, jsonify

# Ensure local package paths are available for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from Yukti_Mobile.Core.automation_engine import AutomationEngine
from Yukti_Mobile.Models.project import ProjectModel
from Yukti_Mobile.Models.user import DB_PATH, UserModel

engine = AutomationEngine()

# -------------------------------
# 📊 LOAD DATA
# -------------------------------

def load_data(file_path):
    df = pd.read_csv(file_path)

    if 'Created Date' in df.columns:
        df['Created Date'] = pd.to_datetime(
            df['Created Date'],
            errors='coerce',
            dayfirst=True   # 🔥 IMPORTANT
        )

    return df

# -------------------------------
# 📅 FILTER DATA (SAFE)
# -------------------------------
def filter_data(df, filter_type, start_date=None, end_date=None):

    if 'Created Date' not in df.columns:
        return df

    today = datetime.today()

    # ✅ TODAY
    if filter_type == "today":
        return df[df['Created Date'].dt.date == today.date()]

    # ✅ THIS WEEK
    elif filter_type == "this_week":
        start = today - timedelta(days=today.weekday())
        return df[
            (df['Created Date'] >= start) &
            (df['Created Date'] <= today)
        ]

    # ✅ THIS MONTH
    elif filter_type == "this_month":
        return df[
            (df['Created Date'].dt.month == today.month) &
            (df['Created Date'].dt.year == today.year)
        ]

    # ✅ LAST MONTH
    elif filter_type == "last_month":
        if today.month == 1:
            last_month = 12
            year = today.year - 1
        else:
            last_month = today.month - 1
            year = today.year

        return df[
            (df['Created Date'].dt.month == last_month) &
            (df['Created Date'].dt.year == year)
        ]

    # ✅ CUSTOM
    elif filter_type == "custom":
        return df[
            (df['Created Date'] >= start_date) &
            (df['Created Date'] <= end_date)
        ]

    return df
    
# -------------------------------
# 🚀 APP START
# -------------------------------
app = Flask(__name__)
automation_engine = engine
app.secret_key = "Yukti_AI_Enterprise_2026"

# -------------------------------
# 🔒 SESSION HELPERS
# -------------------------------
def is_logged_in():
    """Return True if user is logged in (based on session)."""
    return bool(session.get('logged_in'))

# -------------------------------
# 📊 LIVE DATA
# -------------------------------
def get_live_data(filter_type="this_month"):
    output_folder = r"D:\Vipul Personal\CRM Automation work\Old CRM\Master File"

    try:
        files = [f for f in os.listdir(output_folder) if f.endswith(".csv")]

        if not files:
            return 0, {}, "No File"

        files.sort(reverse=True)
        latest_file = files[0]
        file_path = os.path.join(output_folder, latest_file)

        # ✅ Load Data
        df = load_data(file_path)

        # ✅ Apply Filter (safe)
        filtered_df = filter_data(df, filter_type)

        total_leads = len(filtered_df)

        # ✅ Project Count
        project_counts = {}
        if 'Preferred Projects' in filtered_df.columns:
            project_counts = filtered_df['Preferred Projects'].value_counts().to_dict()

        # ✅ Last Run
        last_run = datetime.fromtimestamp(
            os.path.getctime(file_path)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return total_leads, project_counts, last_run

    except Exception as e:
        print(e)
        return 0, {}, "Error"


# -------------------------------
# 🔐 LOGIN
# -------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        if username == "admin" and password == "vipul123":
            session['logged_in'] = True
            return redirect('/')

        else:
            return "❌ Invalid Credentials"

    # GET Request
    return render_template("login.html")
# 🏠 HOME
# -------------------------------
@app.route("/logout")
def logout():
    return redirect(url_for("login"))


@app.route("/")
def dashboard():

    modules = engine.get_all()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()
    cur.execute("SELECT * FROM dashboard_summary WHERE id=1")

    summary = cur.fetchone()

    conn.close()

    print("=" * 60)
    print("Dashboard Refresh")
    print(modules)
    print(summary)
    print("=" * 60)

    return render_template(
        "dashboard.html",
        modules=modules,
        summary=dict(summary)
    )


@app.route("/leads")
def leads():
    return render_template("modules/leads/index.html")


@app.route("/crm")
def crm():
    return render_template("modules/crm/index.html")


@app.route("/automation")
def automation():
    return render_template("modules/automation/index.html")


@app.route("/projects")
def projects():
    model = ProjectModel()

    projects = model.get_all_projects()

    print("Type :", type(projects))
    print("Value:", projects)

    if projects is None:
        print("ProjectModel returned None")
        projects = []

    return render_template(
        "modules/projects/index.html",
        projects=projects
    )

@app.route("/reports")
def reports():
    return render_template("modules/reports/index.html")


@app.route("/analytics")
def analytics():
    return render_template("modules/analytics/index.html")


import sqlite3

@app.route("/users")
def users():

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM users
        ORDER BY first_name
    """)

    users = cur.fetchall()
    
    print("=" * 60)
    print("Total Users:", len(users))
    print(users)
    print("=" * 60)

    conn.close()

    return render_template(
        "modules/users/index.html",
        users=users
    )
    
    print("="*60)
    print(users)
    print(type(users))
    print("="*60)
    

# ============================================================
# 📱 MOBILE APP API - LIVE LEAD DATA
# ============================================================
@app.route("/api/mobile/data", methods=["GET"])
def mobile_live_data():
    """
    Read the same latest Master File used by the Yukti-AI Dashboard
    and expose a small JSON API for the mobile app.

    Query parameters:
      period=today|this_week|this_month|last_month
      project=All|<project name>

    This endpoint is read-only. It does not modify CRM data,
    automation state, or the Master File.
    """
    period = request.args.get("period", "this_month").strip().lower()
    project = request.args.get("project", "All").strip()

    period_map = {
        "today": "today",
        "this week": "this_week",
        "this_week": "this_week",
        "this month": "this_month",
        "this_month": "this_month",
        "last month": "last_month",
        "last_month": "last_month",
    }

    filter_type = period_map.get(period, "this_month")

    output_folder = r"D:\Vipul Personal\CRM Automation work\Old CRM\Master File"

    try:
        files = [
            f for f in os.listdir(output_folder)
            if f.lower().endswith(".csv")
        ]

        if not files:
            return jsonify({
                "success": False,
                "connected": True,
                "message": "No Master File CSV found.",
                "total_leads": 0,
                "today_leads": 0,
                "project_counts": {},
                "last_run": None,
            }), 200

        # Use the newest file by filesystem modification time.
        files.sort(
            key=lambda f: os.path.getmtime(os.path.join(output_folder, f)),
            reverse=True
        )

        latest_file = files[0]
        file_path = os.path.join(output_folder, latest_file)

        df = load_data(file_path)

        # Today's count is always calculated independently.
        today_df = filter_data(df, "today")
        today_leads = len(today_df)

        # Apply selected period.
        filtered_df = filter_data(df, filter_type)

        # Apply selected project.
        if project and project.lower() != "all":
            if "Preferred Projects" in filtered_df.columns:
                selected = project.casefold()
                project_values = (
                    filtered_df["Preferred Projects"]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )
                filtered_df = filtered_df[
                    project_values.str.casefold() == selected
                ]

        total_leads = len(filtered_df)

        project_counts = {}
        if "Preferred Projects" in filtered_df.columns:
            project_counts = {
                str(k): int(v)
                for k, v in filtered_df["Preferred Projects"]
                .fillna("Unknown")
                .astype(str)
                .value_counts()
                .to_dict()
            }

        last_run = datetime.fromtimestamp(
            os.path.getmtime(file_path)
        ).strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            "success": True,
            "connected": True,
            "total_leads": int(total_leads),
            "today_leads": int(today_leads),
            "project_counts": project_counts,
            "selected_period": filter_type,
            "selected_project": project or "All",
            "last_run": last_run,
            "source_file": latest_file,
        }), 200

    except Exception as e:
        print("Mobile API error:", e)
        return jsonify({
            "success": False,
            "connected": True,
            "message": str(e),
            "total_leads": 0,
            "today_leads": 0,
            "project_counts": {},
            "last_run": None,
        }), 500


@app.route("/api/update_status", methods=["POST"])

def update_status():

        data = request.json

        automation = data.get("automation")
        status = data.get("status")
        records = data.get("records", 0)

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor() 

        cur.execute("""
            UPDATE automation_status
            SET
                status=?,
                last_run=?,
                records=?
            WHERE automation_name=?
        """,
        (
            status,
            datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            records,
            automation
        ))

        conn.commit()
        conn.close()

        return jsonify({"success": True})


@app.route("/settings")
def settings():
        return render_template("modules/settings/index.html")


@app.route("/assistant")
def ai():
    return render_template("modules/ai_assistant/index.html")

    filter_type = request.args.get("filter", "this_month")

    total_leads, project_counts, last_run = get_live_data(filter_type)

    project_html = ""
    for k, v in project_counts.items():
        project_html += f"<p>{k}: {v}</p>"

    return f"""
<html>
<body style="background:#0f172a;color:white;text-align:center;padding:20px;">

    <h2>📱 CRM AI Dashboard</h2>

    <!-- ✅ FILTER DROPDOWN -->
    <form method="get">
        <select name="filter" onchange="this.form.submit()" 
            style="padding:10px;border-radius:8px;margin-bottom:15px;">
            
            <option value="today">📅 Today</option>
            <option value="this_week">📆 This Week</option>
            <option value="this_month" selected>📊 This Month</option>
            <option value="last_month">📉 Last Month</option>

        </select>
    </form>

    <!-- LIVE DATA -->
    <div style="background:#1e293b;padding:20px;border-radius:15px;">
        <h3>📊 Live Data</h3>
        <p>Total Leads: {total_leads}</p>
        <p>Last Run: {last_run}</p>
        {project_html}
    </div>

</body>
</html>
"""


# -------------------------------
# 🚀 RUN
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)