import sqlite3

from flask import Flask, render_template, request, redirect, session, url_for
import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from flask import request, jsonify
import json
import re
import hashlib
import secrets
import smtplib
from email.message import EmailMessage

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

# ============================================================
# 📊 IN4 CRM - LEAD ASSIGNED REPORT DATA
# ============================================================
# NEW read-only data source for Yukti-AI mobile/web dashboard.
# It is separate from the existing Old CRM Master File API.
IN4_DB_FILE = r"D:\Yukti-Ai Business Automation\In4 Lead Report Automation\yuktiai_in4.db"


def get_in4_summary(period="this_month", project="All", source="All", user="All"):
    """Read the latest processed In4 Lead Assigned Report from SQLite."""
    if not os.path.exists(IN4_DB_FILE):
        return {
            "success": False,
            "connected": True,
            "message": "In4 report database not found. Run In4_LeadAssignedReport_Automation.py first.",
            "total_leads": 0,
            "today_leads": 0,
            "project_counts": {},
            "source_counts": {},
            "user_counts": {},
            "project_source_counts": {},
            "last_run": None,
        }

    conn = sqlite3.connect(IN4_DB_FILE)
    try:
        df = pd.read_sql_query("SELECT * FROM lead_assignments", conn)
    finally:
        conn.close()

    if df.empty:
        return {
            "success": True,
            "connected": True,
            "data_source": "In4 CRM Lead Assigned Report",
            "message": "In4 report database is empty.",
            "total_leads": 0,
            "today_leads": 0,
            "project_counts": {},
            "source_counts": {},
            "user_counts": {},
            "project_source_counts": {},
            "last_run": None,
        }

    df["Assinged Date"] = pd.to_datetime(df["Assinged Date"], errors="coerce")
    today = datetime.today().date()

    if period == "today":
        period_df = df[df["Assinged Date"].dt.date == today].copy()
    elif period == "this_week":
        start = today - timedelta(days=today.weekday())
        period_df = df[
            (df["Assinged Date"].dt.date >= start) &
            (df["Assinged Date"].dt.date <= today)
        ].copy()
    elif period == "last_month":
        if today.month == 1:
            month, year = 12, today.year - 1
        else:
            month, year = today.month - 1, today.year
        period_df = df[
            (df["Assinged Date"].dt.month == month) &
            (df["Assinged Date"].dt.year == year)
        ].copy()
    else:
        period_df = df[
            (df["Assinged Date"].dt.month == today.month) &
            (df["Assinged Date"].dt.year == today.year)
        ].copy()

    today_df = df[df["Assinged Date"].dt.date == today].copy()

    def apply_filters(frame):
        result = frame.copy()

        if project and project.casefold() != "all":
            values = result["Project Name"].fillna("").astype(str).str.strip()
            result = result[values.str.casefold() == project.casefold()]

        if source and source.casefold() != "all":
            values = result["Enquiry Source"].fillna("").astype(str).str.strip()
            result = result[values.str.casefold() == source.casefold()]

        if user and user.casefold() != "all":
            values = result["Assinged To"].fillna("").astype(str).str.strip()
            result = result[values.str.casefold() == user.casefold()]

        return result

    filtered = apply_filters(period_df)
    filtered_today = apply_filters(today_df)

    def counts(frame, column):
        if column not in frame.columns:
            return {}
        return {
            str(k): int(v)
            for k, v in frame[column]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
                .value_counts()
                .to_dict()
                .items()
        }

    project_source_counts = {}
    for project_name, group in filtered.groupby("Project Name"):
        project_source_counts[str(project_name)] = counts(group, "Enquiry Source")

    return {
        "success": True,
        "connected": True,
        "data_source": "In4 CRM Lead Assigned Report",
        "total_leads": int(len(filtered)),
        "today_leads": int(len(filtered_today)),
        "project_counts": counts(filtered, "Project Name"),
        "source_counts": counts(filtered, "Enquiry Source"),
        "user_counts": counts(filtered, "Assinged To"),
        "project_source_counts": project_source_counts,
        "available_projects": sorted(
            [str(x) for x in df["Project Name"].dropna().unique()]
        ),
        "available_sources": sorted(
            [str(x) for x in df["Enquiry Source"].dropna().unique()]
        ),
        "available_users": sorted(
            [str(x) for x in df["Assinged To"].dropna().unique()]
        ),
        "selected_period": period,
        "selected_project": project or "All",
        "selected_source": source or "All",
        "selected_user": user or "All",
        "last_run": datetime.fromtimestamp(
            os.path.getmtime(IN4_DB_FILE)
        ).strftime("%Y-%m-%d %H:%M:%S"),
    }


@app.route("/api/mobile/in4-data", methods=["GET"])
def mobile_in4_data():
    period = request.args.get("period", "this_month").strip().lower()
    project = request.args.get("project", "All").strip()
    source = request.args.get("source", "All").strip()
    user = request.args.get("user", "All").strip()

    period = {
        "today": "today",
        "this_week": "this_week",
        "this week": "this_week",
        "this_month": "this_month",
        "this month": "this_month",
        "last_month": "last_month",
        "last month": "last_month",
    }.get(period, "this_month")

    try:
        return jsonify(
            get_in4_summary(
                period=period,
                project=project,
                source=source,
                user=user,
            )
        ), 200
    except Exception as e:
        print("In4 Mobile API error:", e)
        return jsonify({
            "success": False,
            "connected": True,
            "message": str(e),
            "total_leads": 0,
            "today_leads": 0,
            "project_counts": {},
            "source_counts": {},
            "user_counts": {},
            "project_source_counts": {},
            "last_run": None,
        }), 500


# ============================================================
# 📱 MOBILE APP API - LEAD RECORDS
# ============================================================
@app.route("/api/mobile/leads", methods=["GET"])
def mobile_leads():
    """
    Read-only lead records from the same In4 SQLite database used by
    the mobile Reports endpoint.

    Filters:
      period=today|yesterday|this_week|this_month|last_month
      project=All|<project>
      source=All|<source>
      user=All|<assigned user>
      search=<free text>
    """
    period = request.args.get("period", "this_month").strip().lower()
    project = request.args.get("project", "All").strip()
    source = request.args.get("source", "All").strip()
    user = request.args.get("user", "All").strip()
    search = request.args.get("search", "").strip()

    period = {
        "today": "today",
        "yesterday": "yesterday",
        "this_week": "this_week",
        "this week": "this_week",
        "this_month": "this_month",
        "this month": "this_month",
        "last_month": "last_month",
        "last month": "last_month",
    }.get(period, "this_month")

    if not os.path.exists(IN4_DB_FILE):
        return jsonify({
            "success": False,
            "message": "In4 report database not found.",
            "leads": [],
            "total_leads": 0,
            "today_leads": 0,
        }), 200

    try:
        conn = sqlite3.connect(IN4_DB_FILE)
        try:
            df = pd.read_sql_query("SELECT * FROM lead_assignments", conn)
        finally:
            conn.close()

        if df.empty:
            return jsonify({
                "success": True,
                "leads": [],
                "total_leads": 0,
                "today_leads": 0,
                "available_projects": [],
                "available_sources": [],
                "available_users": [],
            }), 200

        if "Assinged Date" in df.columns:
            df["Assinged Date"] = pd.to_datetime(
                df["Assinged Date"],
                errors="coerce"
            )

        today = datetime.today().date()

        if period == "today":
            period_df = df[df["Assinged Date"].dt.date == today].copy()
        elif period == "yesterday":
            yesterday = today - timedelta(days=1)
            period_df = df[df["Assinged Date"].dt.date == yesterday].copy()
        elif period == "this_week":
            start = today - timedelta(days=today.weekday())
            period_df = df[
                (df["Assinged Date"].dt.date >= start) &
                (df["Assinged Date"].dt.date <= today)
            ].copy()
        elif period == "last_month":
            if today.month == 1:
                month, year = 12, today.year - 1
            else:
                month, year = today.month - 1, today.year

            period_df = df[
                (df["Assinged Date"].dt.month == month) &
                (df["Assinged Date"].dt.year == year)
            ].copy()
        else:
            period_df = df[
                (df["Assinged Date"].dt.month == today.month) &
                (df["Assinged Date"].dt.year == today.year)
            ].copy()

        today_df = df[df["Assinged Date"].dt.date == today].copy()

        def apply_filters(frame):
            result = frame.copy()

            if project.casefold() != "all" and "Project Name" in result.columns:
                values = result["Project Name"].fillna("").astype(str).str.strip()
                result = result[
                    values.str.casefold() == project.casefold()
                ]

            if source.casefold() != "all" and "Enquiry Source" in result.columns:
                values = result["Enquiry Source"].fillna("").astype(str).str.strip()
                result = result[
                    values.str.casefold() == source.casefold()
                ]

            if user.casefold() != "all" and "Assinged To" in result.columns:
                values = result["Assinged To"].fillna("").astype(str).str.strip()
                result = result[
                    values.str.casefold() == user.casefold()
                ]

            if search:
                searchable_columns = [
                    "Customer Name",
                    "Opportunity ID",
                    "Contact Number",
                    "Project Name",
                    "Enquiry Source",
                    "Assinged To",
                ]

                mask = pd.Series(False, index=result.index)

                for column in searchable_columns:
                    if column in result.columns:
                        mask = mask | result[column].fillna("").astype(str).str.contains(
                            search,
                            case=False,
                            regex=False,
                        )

                result = result[mask]

            return result

        filtered = apply_filters(period_df)
        filtered_today = apply_filters(today_df)

        # Newest leads first.
        if "Assinged Date" in filtered.columns:
            filtered = filtered.sort_values(
                by="Assinged Date",
                ascending=False,
                na_position="last",
            )

        # Keep the mobile response bounded.
        limit = min(
            max(int(request.args.get("limit", "200")), 1),
            500,
        )

        records = []

        for _, row in filtered.head(limit).iterrows():
            def text_value(column):
                if column not in row.index:
                    return ""
                value = row[column]
                if pd.isna(value):
                    return ""
                if isinstance(value, pd.Timestamp):
                    return value.strftime("%Y-%m-%d %H:%M:%S")
                return str(value).strip()

            records.append({
                "Customer Name": text_value("Customer Name"),
                "Opportunity ID": text_value("Opportunity ID"),
                "Contact Number": text_value("Contact Number"),
                "Project Name": text_value("Project Name"),
                "Enquiry Source": text_value("Enquiry Source"),
                "Assinged By": text_value("Assinged By"),
                "Assinged To": text_value("Assinged To"),
                "Assinged Date": text_value("Assinged Date"),
            })

        return jsonify({
            "success": True,
            "connected": True,
            "data_source": "In4 CRM Lead Assigned Report",
            "total_leads": int(len(filtered)),
            "today_leads": int(len(filtered_today)),
            "returned": int(len(records)),
            "leads": records,
            "available_projects": sorted([
                str(x).strip()
                for x in df["Project Name"].dropna().unique()
                if str(x).strip()
            ]) if "Project Name" in df.columns else [],
            "available_sources": sorted([
                str(x).strip()
                for x in df["Enquiry Source"].dropna().unique()
                if str(x).strip()
            ]) if "Enquiry Source" in df.columns else [],
            "available_users": sorted([
                str(x).strip()
                for x in df["Assinged To"].dropna().unique()
                if str(x).strip()
            ]) if "Assinged To" in df.columns else [],
            "last_run": datetime.fromtimestamp(
                os.path.getmtime(IN4_DB_FILE)
            ).strftime("%Y-%m-%d %H:%M:%S"),
        }), 200

    except Exception as e:
        print("Mobile Leads API error:", e)
        return jsonify({
            "success": False,
            "message": str(e),
            "leads": [],
            "total_leads": 0,
            "today_leads": 0,
        }), 500


# ============================================================
# 📱 MOBILE APP API - AUTOMATION STATUS
# ============================================================
@app.route("/api/mobile/automation-status", methods=["GET"])
def mobile_automation_status():
    """
    Read-only automation monitoring endpoint.

    It reads the existing automation_status table. It does not start,
    stop, modify, or redesign any production automation.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row

        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    automation_name,
                    status,
                    last_run,
                    records
                FROM automation_status
                ORDER BY automation_name
            """)
            rows = cur.fetchall()
        finally:
            conn.close()

        automations = []

        for row in rows:
            automations.append({
                "automation_name": row["automation_name"],
                "status": row["status"],
                "last_run": row["last_run"],
                "records": row["records"],
                "error": "",
            })

        return jsonify({
            "success": True,
            "automations": automations,
        }), 200

    except Exception as e:
        print("Mobile Automation Status API error:", e)
        return jsonify({
            "success": False,
            "message": str(e),
            "automations": [],
        }), 200


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

        # Today's count is calculated independently, then the same
        # project filter is applied so the KPI follows the project dropdown.
        today_df = filter_data(df, "today")
        if project and project.lower() != "all" and "Preferred Projects" in today_df.columns:
            selected_today = project.casefold()
            today_values = (
                today_df["Preferred Projects"]
                .fillna("")
                .astype(str)
                .str.strip()
            )
            today_df = today_df[
                today_values.str.casefold() == selected_today
            ]
        today_leads = len(today_df)

        # Apply selected period.
        period_df = filter_data(df, filter_type)

        # Build project counts for the selected period BEFORE applying a
        # project filter, so the mobile dashboard can display all projects.
        all_project_counts = {}
        if "Preferred Projects" in period_df.columns:
            all_project_counts = {
                str(k): int(v)
                for k, v in period_df["Preferred Projects"]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
                .value_counts()
                .to_dict()
                .items()
            }

        # Apply selected project.
        filtered_df = period_df.copy()
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
                .items()
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
            "all_project_counts": all_project_counts,
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


# ============================================================
# MOBILE APP OTP AUTHENTICATION - STEP 1
# ============================================================
OTP_DB_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "mobile_auth.db"
)
OTP_EXPIRY_SECONDS = 300
OTP_MAX_ATTEMPTS = 5
OTP_RESEND_SECONDS = 60

def _otp_db():
    conn = sqlite3.connect(OTP_DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS otp_requests (
            request_id TEXT PRIMARY KEY,
            destination TEXT NOT NULL,
            purpose TEXT NOT NULL,
            otp_hash TEXT NOT NULL,
            created_at REAL NOT NULL,
            expires_at REAL NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            verified INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    return conn

def _hash_otp(otp):
    return hashlib.sha256(otp.encode("utf-8")).hexdigest()

def _looks_like_email(value):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value))

def _looks_like_mobile(value):
    return bool(re.match(r"^\+?[0-9][0-9\s\-]{7,18}$", value))

def _send_otp_email(destination, otp):
    host = os.getenv("YUKTI_OTP_SMTP_HOST", "").strip()
    port = int(os.getenv("YUKTI_OTP_SMTP_PORT", "587"))
    user = os.getenv("YUKTI_OTP_SMTP_USER", "").strip()
    password = os.getenv("YUKTI_OTP_SMTP_PASSWORD", "")
    from_email = os.getenv("YUKTI_OTP_FROM_EMAIL", user).strip()
    use_tls = os.getenv("YUKTI_OTP_SMTP_TLS", "true").strip().lower() in (
        "1", "true", "yes"
    )

    if not host or not user or not password or not from_email:
        raise RuntimeError("Email OTP delivery is not configured on the server.")

    message = EmailMessage()
    message["Subject"] = "Yukti-AI Security Verification OTP"
    message["From"] = from_email
    message["To"] = destination
    message.set_content(
        f"Your Yukti-AI verification OTP is: {otp}\n\n"
        "This OTP is valid for 5 minutes.\n"
        "If you did not request this code, please ignore this email."
    )

    # Gmail supports implicit SSL on port 465 and STARTTLS on port 587.
    if port == 465:
        with smtplib.SMTP_SSL(host, port, timeout=15) as smtp:
            smtp.login(user, password)
            smtp.send_message(message)
    else:
        with smtplib.SMTP(host, port, timeout=15) as smtp:
            if use_tls:
                smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(message)

def _send_otp_sms(destination, otp):
    raise RuntimeError(
        "Mobile OTP delivery is not configured yet. "
        "Email OTP is available after SMTP configuration."
    )

@app.route("/api/mobile/auth/otp/request", methods=["POST"])
def mobile_auth_otp_request():
    try:
        data = request.get_json(silent=True) or {}
        destination = str(data.get("destination", "")).strip()
        purpose = str(data.get("purpose", "settings_2fa")).strip()

        if not destination:
            return jsonify({
                "success": False,
                "message": "Mobile number or email address is required."
            }), 400

        is_email = _looks_like_email(destination)
        is_mobile = _looks_like_mobile(destination)

        if not is_email and not is_mobile:
            return jsonify({
                "success": False,
                "message": "Enter a valid email address or mobile number."
            }), 400

        import time
        now = time.time()
        conn = _otp_db()

        try:
            destination_key = destination.casefold() if is_email else destination
            recent = conn.execute("""
                SELECT created_at
                FROM otp_requests
                WHERE destination = ? AND purpose = ? AND verified = 0
                ORDER BY created_at DESC LIMIT 1
            """, (destination_key, purpose)).fetchone()

            if recent and now - float(recent["created_at"]) < OTP_RESEND_SECONDS:
                wait_for = int(OTP_RESEND_SECONDS - (now - float(recent["created_at"])))
                return jsonify({
                    "success": False,
                    "message": f"Please wait {max(wait_for, 1)} seconds before requesting another OTP."
                }), 429

            otp = f"{secrets.randbelow(1000000):06d}"
            request_id = secrets.token_urlsafe(24)

            conn.execute("""
                INSERT INTO otp_requests (
                    request_id, destination, purpose, otp_hash,
                    created_at, expires_at, attempts, verified
                )
                VALUES (?, ?, ?, ?, ?, ?, 0, 0)
            """, (
                request_id, destination_key, purpose, _hash_otp(otp),
                now, now + OTP_EXPIRY_SECONDS
            ))
            conn.commit()
        finally:
            conn.close()

        try:
            if is_email:
                _send_otp_email(destination, otp)
            else:
                _send_otp_sms(destination, otp)
        except Exception as delivery_error:
            conn = _otp_db()
            try:
                conn.execute("DELETE FROM otp_requests WHERE request_id = ?", (request_id,))
                conn.commit()
            finally:
                conn.close()

            print("OTP delivery error:", delivery_error)
            return jsonify({
                "success": False,
                "message": str(delivery_error),
            }), 503

        return jsonify({
            "success": True,
            "message": "OTP sent successfully.",
            "request_id": request_id,
            "expires_in": OTP_EXPIRY_SECONDS,
            "delivery": "email" if is_email else "sms",
        }), 200

    except Exception as e:
        print("OTP request API error:", e)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/mobile/auth/otp/verify", methods=["POST"])
def mobile_auth_otp_verify():
    try:
        data = request.get_json(silent=True) or {}
        destination = str(data.get("destination", "")).strip()
        otp = str(data.get("otp", "")).strip()
        request_id = str(data.get("request_id", "")).strip()
        purpose = str(data.get("purpose", "settings_2fa")).strip()

        if not destination or not request_id:
            return jsonify({
                "success": False,
                "message": "OTP verification request is incomplete."
            }), 400

        if not re.match(r"^\d{6}$", otp):
            return jsonify({
                "success": False,
                "message": "Enter the 6-digit OTP."
            }), 400

        conn = _otp_db()
        try:
            row = conn.execute("""
                SELECT * FROM otp_requests
                WHERE request_id = ? AND purpose = ? LIMIT 1
            """, (request_id, purpose)).fetchone()

            if not row:
                return jsonify({
                    "success": False,
                    "message": "OTP request was not found or has expired."
                }), 404

            import time
            now = time.time()

            if int(row["verified"]) == 1:
                return jsonify({
                    "success": False,
                    "message": "This OTP has already been used."
                }), 400

            if now > float(row["expires_at"]):
                return jsonify({
                    "success": False,
                    "message": "OTP has expired. Please request a new OTP."
                }), 400

            attempts = int(row["attempts"])
            if attempts >= OTP_MAX_ATTEMPTS:
                return jsonify({
                    "success": False,
                    "message": "Too many incorrect attempts. Please request a new OTP."
                }), 429

            submitted_destination = (
                destination.casefold()
                if _looks_like_email(destination)
                else destination
            )

            if str(row["destination"]).strip() != submitted_destination:
                return jsonify({
                    "success": False,
                    "message": "OTP destination does not match the request."
                }), 400

            if _hash_otp(otp) != str(row["otp_hash"]):
                conn.execute("""
                    UPDATE otp_requests
                    SET attempts = attempts + 1
                    WHERE request_id = ?
                """, (request_id,))
                conn.commit()

                remaining = max(OTP_MAX_ATTEMPTS - attempts - 1, 0)
                return jsonify({
                    "success": False,
                    "message": f"Incorrect OTP. {remaining} attempts remaining."
                }), 400

            conn.execute("""
                UPDATE otp_requests SET verified = 1
                WHERE request_id = ?
            """, (request_id,))
            conn.commit()

            return jsonify({
                "success": True,
                "message": "OTP verified successfully.",
                "verified": True,
            }), 200
        finally:
            conn.close()

    except Exception as e:
        print("OTP verify API error:", e)
        return jsonify({"success": False, "message": str(e)}), 500

# -------------------------------
# 🚀 RUN
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)