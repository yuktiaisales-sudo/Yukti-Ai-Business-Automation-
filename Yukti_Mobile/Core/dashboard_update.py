import os
import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "Database",
        "yukti.db"
    )
)

MASTER_FOLDER = r"D:\IT Pacifica\CRM\Leads Work\Year 2026 Leads\Master Files"


def read_csv_file(file_path):

    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1"]

    for enc in encodings:
        try:
            return pd.read_csv(file_path, encoding=enc)
        except UnicodeDecodeError:
            continue

    raise Exception(f"Cannot read CSV : {file_path}")


def get_total_leads(master_folder):

    total = 0

    for file in os.listdir(master_folder):

        full_file = os.path.join(master_folder, file)

        if not os.path.isfile(full_file):
            continue

        if file.startswith("Old CRM CSV Final Structure") and file.endswith(".csv"):

            df = read_csv_file(full_file)
            total += len(df)

        elif file.startswith("In4 CRM CSV Final Structure") and file.endswith(".csv"):

            df = read_csv_file(full_file)
            total += len(df)

    return total



def count_valid_leads(df, mobile_columns):

    for col in mobile_columns:

        if col in df.columns:

            mobile = (
                df[col]
                .fillna("")
                .astype(str)
                .str.replace(r"\D", "", regex=True)
            )

            return mobile.str.len().ge(10).sum()

    return 0


def update_dashboard(
    today_folder,
    automation_name=None,
    automation_status="Completed",
    records=0
):
    print("=" * 60)
    print("Updating Dashboard")
    print("Today Folder =", today_folder)
    print("Files Found =", os.listdir(today_folder))
    print("=" * 60)
    
    print("USING FILE:", __file__)


    # Connect to DB early so we can read existing summary
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    today_leads = records

    cur.execute("SELECT total_leads FROM dashboard_summary WHERE id=1")
    row = cur.fetchone()

    previous_total = row[0] if row else 0

    total_leads = previous_total + today_leads

    crm_uploaded = today_leads
    pending_upload = 0

    print("=" * 60)
    print("DB PATH :", DB_PATH)
    print("TODAY FOLDER :", today_folder)
    print("=" * 60)
    print("Updating SQLite...")
    
    
    crm_uploaded = today_leads
    pending_upload = max(total_leads - today_leads, 0)

    cur.execute("""
        UPDATE dashboard_summary
        SET
            total_leads = ?,
            today_leads = ?,
            crm_uploaded = ?,
            pending_upload = ?,
            last_updated = datetime('now')
        WHERE id = 1
    """,
    (
        total_leads,
        today_leads,
        crm_uploaded,
        pending_upload
    ))

    # ----------------------------------------------------
    # Update Automation Status
    # ----------------------------------------------------

    if automation_name:

        cur.execute("""
            UPDATE automation_status
            SET
                status=?,
                last_run=?,
                records=?
            WHERE automation_name=?
        """,
        (
            automation_status,
            datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            records,
            automation_name
        ))
        
        cur.execute("""
        INSERT INTO activity_log
        (
            activity_name,
            status,
            records,
            start_time,
            end_time,
            remarks
        )
        VALUES
        (
            ?,?,?,?,?,'Completed Successfully'
        )
    """,
    (
        automation_name,
        automation_status,
        records,
        datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    ))
                                
        
        print("Project Summary Updated Successfully")
        
                  
        
        
# ===========================================
# UPDATE PROJECT SUMMARY
# ===========================================

        print("Updating Project Summary...")

        master_file = None

        for file in os.listdir(MASTER_FOLDER):
            if file.endswith(".csv"):
                master_file = os.path.join(MASTER_FOLDER, file)

        if master_file:

            df = read_csv_file(master_file)
            
            print("Master File =", master_file)
            print(df.columns.tolist())

            # Clean blanks
            df["Project Name"] = df["Project Name"].fillna("Unknown")
            df["Source Of Information"] = df["Source Of Information"].fillna("Other")

            projects = df["Project Name"].unique()

            # Clear previous data
            cur.execute("DELETE FROM project_summary")

            for project in projects:

                project_df = df[df["Project Name"] == project]

                total = len(project_df)

                facebook = len(project_df[project_df["Source Of Information"].str.contains("facebook", case=False, na=False)])

                instagram = len(project_df[project_df["Source Of Information"].str.contains("instagram", case=False, na=False)])

                website = len(project_df[project_df["Source Of Information"].str.contains("website", case=False, na=False)])

                google = len(project_df[project_df["Source Of Information"].str.contains("google", case=False, na=False)])

                housing = len(project_df[project_df["Source Of Information"].str.contains("housing", case=False, na=False)])

                magicbricks = len(project_df[project_df["Source Of Information"].str.contains("magic", case=False, na=False)])

                acres99 = len(project_df[project_df["Source Of Information"].str.contains("99", case=False, na=False)])

                walkin = len(project_df[project_df["Source Of Information"].str.contains("walk", case=False, na=False)])

                email_campaign = len(project_df[project_df["Source Of Information"].str.contains("email", case=False, na=False)])

                live_chat = len(project_df[project_df["Source Of Information"].str.contains("chat", case=False, na=False)])

                other = total - (
                    facebook + instagram + website + google +
                    housing + magicbricks + acres99 +
                    walkin + email_campaign + live_chat
                )

                cur.execute("""
                INSERT INTO project_summary
                (
                    project_name,
                    today_leads,
                    total_leads,
                    facebook,
                    instagram,
                    website,
                    google,
                    live_chat,
                    email_campaign,
                    walkin,
                    housing,
                    magicbricks,
                    source_99acres,
                    other,
                    last_updated
                )
                VALUES
                (
                    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now')
                )
                """,
                (
                    project,
                    total,
                    total,
                    facebook,
                    instagram,
                    website,
                    google,
                    live_chat,
                    email_campaign,
                    walkin,
                    housing,
                    magicbricks,
                    acres99,
                    other
                ))

            conn.commit()

        print("Project Summary Updated")
        
        conn.commit()
        conn.close()

        print("SQLite Updated Successfully")
        print("Commit Successful")
        
                      
    print("Dashboard Update Completed")
    
    return today_leads
  

if __name__ == "__main__":

    today_folder = r"D:\IT Pacifica\CRM\Leads Work\Year 2026 Leads\13 July 2026"
    # calculate records from master folder if needed
    records = get_total_leads(MASTER_FOLDER)

    update_dashboard(
        today_folder,
        automation_name="Outlook Email Reader",
        automation_status="Completed",
        records=records
    )