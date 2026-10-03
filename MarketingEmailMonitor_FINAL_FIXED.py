# ============================================================
# YUKTI-AI MARKETING EMAIL MONITOR
# ============================================================
# Watches Outlook -> Inbox -> Mahek Chopra - Leads.
# If a TODAY email from mchopra@pacificacompanies.in
# contains a CSV attachment, it launches OutlookExcelAutomation.py.
# This monitor does not process/download leads or run Power BI/CRM.
# ============================================================

import os
import sys
import json
import time
import subprocess
from datetime import datetime

import pythoncom
import win32com.client
from datetime import datetime, timedelta


# ============================================================
# CONFIGURATION
# ============================================================

OUTLOOK_FOLDER_NAME = "Mahek Chopra - Leads"
MARKETING_SENDER = "mchopra@pacificacompanies.in"
CHECK_INTERVAL = 60

# Date control
# "today" = only today; "yesterday" = yesterday; "custom" = CUSTOM_DATE
MODE = "today"
CUSTOM_DATE = "08-09-2026"

def get_target_date():
    if MODE == "today":
        return datetime.now().date()
    elif MODE == "yesterday":
        return (datetime.now() - timedelta(days=1)).date()
    elif MODE == "custom":
        return datetime.strptime(CUSTOM_DATE, "%d-%m-%Y").date()
    else:
        raise ValueError('Invalid MODE. Use: "today", "yesterday", or "custom"')


# Both Python files are in the same Mobile App folder.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

MAIN_AUTOMATION = os.path.join(
    SCRIPT_DIR,
    "OutlookExcelAutomation.py"
)

PROCESSED_FILE = os.path.join(
    SCRIPT_DIR,
    "processed_marketing_emails.json"
)


# ============================================================
# PROCESSED EMAIL STATE
# ============================================================

def load_processed_emails():
    if not os.path.exists(PROCESSED_FILE):
        return set()

    try:
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return set(data) if isinstance(data, list) else set()

    except Exception as e:
        print(f"Processed email file warning: {e}")
        return set()


def save_processed_emails(processed_emails):
    try:
        with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(processed_emails), f, indent=2)

    except Exception as e:
        print(f"Could not save processed emails: {e}")


# ============================================================
# OUTLOOK CONNECTOR
# ============================================================
# Uses the same proven connection method as the working
# OutlookExcelAutomation.py:
# Dispatch -> MAPI -> Inbox.
# ============================================================

def connect_to_outlook():
    """
    Create a fresh Outlook COM connection for each monitoring cycle.

    COM is initialized once for the lifetime of monitor().
    This function therefore does NOT call CoInitialize/CoUninitialize.
    """
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        inbox = namespace.GetDefaultFolder(6)  # Inbox

        return outlook, namespace, inbox

    except Exception as e:
        print(f"Outlook connection failed: {e}")
        return None, None, None

# ============================================================
# FIND MAHEK CHOPRA - LEADS FOLDER
# ============================================================
# Searches direct Inbox subfolders using the same proven
# "mahek" + "lead" matching used by the working automation.
# ============================================================

def get_mahek_chopra_leads_folder(inbox):
    try:
        for folder in inbox.Folders:

            name = folder.Name.strip().lower()

            if "mahek" in name and "lead" in name:
                print(f"Using Outlook folder: {folder.Name}")
                return folder

        print(
            f"ERROR: Outlook folder not found: "
            f"{OUTLOOK_FOLDER_NAME}"
        )
        return None

    except Exception as e:
        print(f"Folder detection error: {e}")
        return None


# ============================================================
# GET SENDER EMAIL
# ============================================================

def get_sender_email(message):
    try:
        sender = str(
            getattr(message, "SenderEmailAddress", "")
        ).strip().lower()

        if "@" in sender:
            return sender

        # Exchange fallback
        try:
            smtp_address = message.PropertyAccessor.GetProperty(
                "http://schemas.microsoft.com/mapi/proptag/0x39FE001E"
            )

            if smtp_address:
                return str(smtp_address).strip().lower()

        except Exception:
            pass

        return sender

    except Exception:
        return ""


# ============================================================
# CSV ATTACHMENT CHECK
# ============================================================

def has_csv_attachment(message):
    try:
        attachments = message.Attachments

        for i in range(1, attachments.Count + 1):
            attachment = attachments.Item(i)

            filename = str(
                attachment.FileName
            ).strip().lower()

            if filename.endswith(".csv"):
                return True

    except Exception:
        pass

    return False


# ============================================================
# CHECK WHETHER MAIN AUTOMATION IS ALREADY RUNNING
# ============================================================

def is_main_automation_running():

    try:

        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            (
                "Get-CimInstance Win32_Process "
                "| Where-Object { "
                "($_.Name -eq 'python.exe' -or $_.Name -eq 'pythonw.exe') "
                "-and $_.CommandLine -like '*OutlookExcelAutomation.py*' "
                "} "
                "| Select-Object -ExpandProperty ProcessId"
            )
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )

        # Only Python/PythonW processes running the actual
        # OutlookExcelAutomation.py are considered.
        return bool(result.stdout.strip())

    except Exception as e:

        print(
            f"Process check warning: {e}"
        )

        return False

# ============================================================
# START MAIN AUTOMATION
# ============================================================

def start_main_automation():

    print()
    print("=" * 60)
    print("STARTING OUTLOOK EXCEL AUTOMATION")
    print("=" * 60)

    if not os.path.isfile(MAIN_AUTOMATION):
        print("ERROR: Main automation file not found:")
        print(MAIN_AUTOMATION)
        return False

    try:
        process = subprocess.Popen(
            [sys.executable, MAIN_AUTOMATION],
            cwd=SCRIPT_DIR
        )

        print("OutlookExcelAutomation.py started successfully.")
        print(f"Python executable : {sys.executable}")
        print(f"Automation path   : {MAIN_AUTOMATION}")
        print(f"Process ID        : {process.pid}")
        print()
        print("Monitor is now WAITING for OutlookExcelAutomation.py")
        print("to finish before stopping automatically.")
        print("=" * 60)

        # IMPORTANT:
        # Do not continue the monitor loop.
        # Wait until the production automation finishes.
        return_code = process.wait()

        print()
        print("=" * 60)
        print("OUTLOOK EXCEL AUTOMATION FINISHED")
        print(f"Process ID        : {process.pid}")
        print(f"Return code       : {return_code}")
        print("=" * 60)

        return return_code == 0

    except Exception as e:
        print(f"ERROR starting/waiting for main automation: {e}")
        return False


# ============================================================
# CHECK TODAY'S MARKETING EMAILS
# ============================================================

def check_for_marketing_emails(
    target_folder,
    processed_emails
):

    target_only_date = get_target_date()
    qualifying_emails = []

    try:
        messages = target_folder.Items

        try:
            messages.Sort("[ReceivedTime]", True)
        except Exception:
            pass

        for msg in messages:

            try:

                if not hasattr(msg, "ReceivedTime"):
                    continue

                received_time = msg.ReceivedTime
                received_date = received_time.date()

                # ------------------------------------------------
                # TARGET DATE ONLY
                # ------------------------------------------------
                if received_date != target_only_date:
                    continue

                # ------------------------------------------------
                # MARKETING SENDER ONLY
                # ------------------------------------------------
                sender = get_sender_email(msg)

                if sender != MARKETING_SENDER.lower():
                    continue

                # ------------------------------------------------
                # MARKETING SUBJECTS
                # ------------------------------------------------
                subject = str(
                    getattr(msg, "Subject", "")
                ).strip()

                subject_lower = subject.lower()

                if (
                    "lead" not in subject_lower
                    and "brochure download" not in subject_lower
                ):
                    continue

                # ------------------------------------------------
                # CSV REQUIRED
                # ------------------------------------------------
                if not has_csv_attachment(msg):
                    continue

                # ------------------------------------------------
                # ENTRY ID / DUPLICATE PROTECTION
                # ------------------------------------------------
                entry_id = str(msg.EntryID)

                if entry_id in processed_emails:
                    continue

                qualifying_emails.append({
                    "entry_id": entry_id,
                    "subject": subject,
                    "sender": sender,
                    "received_time": received_time
                })

            except Exception as e:
                print(f"Error processing Outlook item: {e}")
                continue

        # --------------------------------------------------------
        # NO NEW EMAILS
        # --------------------------------------------------------
        if not qualifying_emails:
            return False

        # --------------------------------------------------------
        # SHOW ALL NEW EMAILS FOUND
        # --------------------------------------------------------
        print()
        print("=" * 60)
        print("NEW MARKETING EMAILS DETECTED")
        print("=" * 60)
        print(f"New qualifying emails: {len(qualifying_emails)}")

        for item in qualifying_emails:
            print()
            print(f"Subject : {item['subject']}")
            print(f"Sender  : {item['sender']}")
            print(f"Received: {item['received_time']}")
            print("CSV attachment: YES")

        print("=" * 60)

        # --------------------------------------------------------
        # LAUNCH ONCE FOR THE WHOLE BATCH
        # AND WAIT UNTIL IT FINISHES.
        # --------------------------------------------------------
        print()
        print(
            "Launching OutlookExcelAutomation.py once "
            "for the detected email batch..."
        )

        started_and_finished_ok = start_main_automation()

        # --------------------------------------------------------
        # MARK ALL DETECTED EMAILS AS PROCESSED ONLY AFTER
        # THE PRODUCTION AUTOMATION HAS FINISHED SUCCESSFULLY.
        # --------------------------------------------------------
        if started_and_finished_ok:

            for item in qualifying_emails:
                processed_emails.add(item["entry_id"])

            save_processed_emails(processed_emails)

            print()
            print("=" * 60)
            print("ALL DETECTED EMAILS MARKED AS PROCESSED")
            print(f"Processed this run: {len(qualifying_emails)}")
            print("=" * 60)

            return True

        print()
        print(
            "Production automation did not finish successfully."
        )
        print(
            "Emails were NOT marked as processed."
        )

        return False

    except Exception as e:
        print(f"Email scan error: {e}")
        return False


# ============================================================
# MAIN MONITOR LOOP
# ============================================================

def monitor():
    """
    Run the marketing email monitor.

    Outlook COM is initialized once for the lifetime of this monitor.
    Each 60-second cycle creates a fresh Outlook COM connection.
    """

    pythoncom.CoInitialize()

    try:
        processed_emails = load_processed_emails()

        print(
            f"Processed email records: "
            f"{len(processed_emails)}"
        )

        while True:

            outlook = None
            namespace = None
            inbox = None
            target_folder = None

            try:
                # Create a fresh Outlook connection for this cycle.
                outlook, namespace, inbox = connect_to_outlook()

                if inbox is None:
                    print(
                        "Outlook unavailable. "
                        "Will retry in 60 seconds."
                    )

                else:
                    target_folder = get_mahek_chopra_leads_folder(inbox)

                    if target_folder is None:
                        print(
                            "Mahek Chopra - Leads folder "
                            "not available. "
                            "Will retry in 60 seconds."
                        )

                    else:
                        completed = check_for_marketing_emails(
                            target_folder,
                            processed_emails
                        )

                        # Once the production automation has finished
                        # successfully, STOP this monitor automatically.
                        if completed:
                            print()
                            print("=" * 60)
                            print("MARKETING EMAIL MONITOR STOPPED")
                            print("Reason: automation completed successfully.")
                            print("=" * 60)
                            return

            except Exception as e:
                print(f"Monitor error: {e}")

            finally:
                # Release COM references before the next cycle.
                target_folder = None
                inbox = None
                namespace = None
                outlook = None

            print()
            print(
                f"Next Outlook check in "
                f"{CHECK_INTERVAL} seconds..."
            )

            time.sleep(CHECK_INTERVAL)

    finally:
        # COM is initialized once above and released only when
        # the monitor actually exits.
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass

# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("YUKTI-AI MARKETING EMAIL MONITOR")
    print("=" * 60)
    print(f"Monitor folder      : {OUTLOOK_FOLDER_NAME}")
    print(f"Marketing sender    : {MARKETING_SENDER}")
    print(f"Main automation     : {MAIN_AUTOMATION}")
    print(f"Check interval      : {CHECK_INTERVAL} seconds")
    print("=" * 60)

    print()
    print("=" * 60)
    print("MONITOR IS RUNNING")
    print("=" * 60)
    print(
        f"Watching Outlook folder : "
        f"{OUTLOOK_FOLDER_NAME}"
    )
    print(
        f"Marketing sender        : "
        f"{MARKETING_SENDER}"
    )
    print(
        f"Check interval          : "
        f"{CHECK_INTERVAL} seconds"
    )
    print()
    print("Monitor is running...")
    print("Press CTRL+C to stop.")
    print("=" * 60)

    try:
        monitor()

    except KeyboardInterrupt:
        print()
        print("=" * 60)
        print("MARKETING EMAIL MONITOR STOPPED")
        print("=" * 60)
