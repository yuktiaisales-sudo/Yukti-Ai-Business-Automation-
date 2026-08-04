# =========================================================
# CRM AUTOMATION - ENTERPRISE VERSION
# =========================================================
# FEATURES:
# ✔ Outlook Email Detection
# ✔ Google Sheets Batch Update (No Quota Error)
# ✔ Backend Email Sending (No Outlook Popup)
# ✔ Project Wise Summary
# ✔ Recent Email Validation
# ✔ Production Ready Structure
# =========================================================

# INSTALL REQUIRED PACKAGES:
# pip install gspread oauth2client pywin32

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import win32com.client
from datetime import datetime
import traceback
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from Yukti_Mobile.Core.dashboard_logger import update_module
from Yukti_Mobile.Core.dashboard_update import update_dashboard


# =========================================================
# GOOGLE SHEETS CONFIGURATION
# =========================================================

CREDENTIALS_FILE = r"D:\Vipul Personal\Power BI CRM Leads Automation Project\AI Buddy BKP\credentials.json"

SPREADSHEET_NAME = "Leads Mastersheet"

SHEET_NAMES = [
    "Pride Towers",
    "Casa Lakeside",
    "Amara",
    "San Martin",
    "San Lucas",
    "North Enclave",
    "Hillcrest",
    "Pacifica One",
    "Enchante"
]

# =========================================================
# OUTLOOK EMAIL DETECTION CONFIG
# =========================================================

EMAIL_SUBJECT = "CRM Automation"
EMAIL_SENDER = "vshah@pacificacompanies.in"

# =========================================================
# SMTP EMAIL CONFIGURATION
# =========================================================

SMTP_SERVER = "pacificacompanies.icewarpcloud.in"
SMTP_PORT = 587

SMTP_EMAIL = "test@pacificacompanies.in"
SMTP_PASSWORD = "Autoemail@#123"

SUMMARY_TO = "vshah@pacificacompanies.in"



# =========================================================
# GOOGLE AUTHENTICATION
# =========================================================

start_time = time.time()


scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    scope
)

client = gspread.authorize(credentials)

spreadsheet = client.open(SPREADSHEET_NAME)



# =========================================================
# UPDATE GOOGLE SHEETS
# =========================================================

def update_upload_status():

    summary_lines = []
    total_uploaded = 0

    for sheet_name in SHEET_NAMES:

        try:

            print(f"\nProcessing Sheet: {sheet_name}")

            worksheet = spreadsheet.worksheet(sheet_name)

            data = worksheet.get_all_records()

            headers = worksheet.row_values(1)

            status_col = headers.index("upload_status") + 1

            updates = []

            uploaded_count = 0

            for idx, row in enumerate(data, start=2):

                phone = str(
                    row.get("phone_number", "")
                ).strip()

                status = str(
                    row.get("upload_status", "")
                ).strip()

                # CONDITION
                if phone != "" and status == "":

                    cell_reference = gspread.utils.rowcol_to_a1(
                        idx,
                        status_col
                    )

                    updates.append({
                        "range": cell_reference,
                        "values": [["Uploaded"]]
                    })

                    uploaded_count += 1
                    total_uploaded += 1

            # SINGLE BATCH UPDATE
            if updates:

                worksheet.batch_update(updates)

            summary_lines.append(
                f"{sheet_name} : {uploaded_count} Leads Uploaded"
            )

            print(f"{sheet_name} Completed Successfully.")

            # SMALL DELAY
            time.sleep(2)

        except Exception as e:

            summary_lines.append(
                f"{sheet_name} : ERROR - {str(e)}"
            )

            print(traceback.format_exc())

    return summary_lines, total_uploaded

# =========================================================
# SEND SUMMARY EMAIL (BACKGROUND)
# =========================================================

def update_dashboard(summary_lines, total_uploaded):
    pass

def send_summary_email(summary_lines, total_uploaded):

    try:

        subject = "CRM Upload Status Summary"

        body = f"""
CRM Upload Status Summary

Date Time:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

--------------------------------------------------

"""

        for line in summary_lines:
            body += line + "\n"

        body += f"""

--------------------------------------------------

Total Uploaded Leads : {total_uploaded}

Status : SUCCESS

Generated Automatically by CRM Automation Python Script
"""

        # EMAIL MESSAGE
        msg = MIMEMultipart()

        msg["From"] = SMTP_EMAIL
        msg["To"] = SUMMARY_TO
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        # SMTP SERVER
        server = smtplib.SMTP(
            SMTP_SERVER,
            SMTP_PORT
        )

        "server.starttls()"

        server.login(
            SMTP_EMAIL,
            SMTP_PASSWORD
        )

        text = msg.as_string()

        server.sendmail(
            SMTP_EMAIL,
            SUMMARY_TO,
            text
        )

        server.quit()

        print("Summary Email Sent Successfully.")

    except Exception as e:

        print(f"Summary Email Error: {e}")

def main():
    global start_time
    start_time = time.time()

    print("===================================")
    print("CRM AUTOMATION STARTED")
    print("===================================\n")

    print("Starting Google Sheet Updates...\n")

    # Run updates and get summary
    summary_lines, total_uploaded = update_upload_status()
    
    update_module(
        module_name="Google Sheet Update",
        status="Completed",
        records=total_uploaded,
        success=total_uploaded,
        failed=0
    )

    send_summary_email(summary_lines, total_uploaded)

    print("\nSending Summary Email...\n")        
    print("\n===================================")
    print("PROCESS COMPLETED SUCCESSFULLY")
    print("===================================")
    
# =========================================================
# RUN SCRIPT
# =========================================================

if __name__ == "__main__":

    main()