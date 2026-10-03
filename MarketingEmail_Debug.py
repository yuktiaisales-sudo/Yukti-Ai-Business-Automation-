# ============================================================
# YUKTI-AI MARKETING EMAIL DEBUG
# ============================================================
# Diagnostic only.
# Does NOT launch OutlookExcelAutomation.py.
# Inspects the latest emails in:
#     Outlook -> Inbox -> Mahek Chopra - Leads
# and shows exactly which monitor condition passes/fails.
# ============================================================

import os
import sys
from datetime import datetime, timedelta

import pythoncom
import win32com.client


OUTLOOK_FOLDER_NAME = "Mahek Chopra - Leads"
MARKETING_SENDER = "mchopra@pacificacompanies.in"

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
        raise ValueError("Invalid MODE")


def get_sender_email(message):
    try:
        sender = str(
            getattr(message, "SenderEmailAddress", "")
        ).strip().lower()

        if "@" in sender:
            return sender

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


def get_csv_attachments(message):
    files = []

    try:
        attachments = message.Attachments

        for i in range(1, attachments.Count + 1):
            attachment = attachments.Item(i)
            filename = str(
                attachment.FileName
            ).strip()

            if filename.lower().endswith(".csv"):
                files.append(filename)

    except Exception as e:
        print(f"CSV attachment inspection error: {e}")

    return files


def main():

    print("=" * 70)
    print("YUKTI-AI MARKETING EMAIL DEBUG")
    print("=" * 70)

    target_date = get_target_date()

    print(f"Python          : {sys.executable}")
    print(f"Folder          : {OUTLOOK_FOLDER_NAME}")
    print(f"Sender          : {MARKETING_SENDER}")
    print(f"Date MODE       : {MODE}")
    print(f"Target date     : {target_date}")
    print("=" * 70)

    pythoncom.CoInitialize()

    try:

        print("\nConnecting to Outlook...")

        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        inbox = namespace.GetDefaultFolder(6)

        print("✅ Outlook connection: PASS")
        print(f"Inbox: {inbox.Name}")

        target_folder = None

        for folder in inbox.Folders:
            name = folder.Name.strip().lower()

            if "mahek" in name and "lead" in name:
                target_folder = folder
                break

        if target_folder is None:
            print("❌ TARGET FOLDER NOT FOUND")
            return

        print(f"✅ Target folder: {target_folder.Name}")

        messages = target_folder.Items
        messages.Sort("[ReceivedTime]", True)

        print(f"Total messages: {messages.Count}")
        print("\n" + "=" * 70)
        print("CHECKING LATEST 10 EMAILS")
        print("=" * 70)

        checked = 0

        for i in range(1, min(messages.Count, 10) + 1):

            try:

                msg = messages.Item(i)

                subject = str(
                    getattr(msg, "Subject", "")
                ).strip()

                sender = get_sender_email(msg)

                received_time = getattr(
                    msg,
                    "ReceivedTime",
                    None
                )

                received_date = (
                    received_time.date()
                    if received_time is not None
                    else None
                )

                unread = getattr(
                    msg,
                    "UnRead",
                    None
                )

                entry_id = str(
                    getattr(msg, "EntryID", "")
                )

                csv_files = get_csv_attachments(msg)

                print("\n" + "-" * 70)
                print(f"EMAIL #{i}")
                print("-" * 70)

                print(f"Subject          : {subject}")
                print(f"Sender           : {sender}")
                print(f"Received         : {received_time}")
                print(f"Received date    : {received_date}")
                print(f"Unread           : {unread}")
                print(f"CSV attachments  : {csv_files}")
                print(f"EntryID exists   : {'YES' if entry_id else 'NO'}")

                # -------------------------------
                # DATE CHECK
                # -------------------------------
                date_pass = (
                    received_date == target_date
                )

                print(
                    f"DATE CHECK       : "
                    f"{'PASS ✅' if date_pass else 'FAIL ❌'}"
                )

                # -------------------------------
                # SENDER CHECK
                # -------------------------------
                sender_pass = (
                    sender == MARKETING_SENDER.lower()
                )

                print(
                    f"SENDER CHECK     : "
                    f"{'PASS ✅' if sender_pass else 'FAIL ❌'}"
                )

                # -------------------------------
                # SUBJECT CHECK
                # -------------------------------
                subject_lower = subject.lower()

                subject_pass = (
                    "lead" in subject_lower
                    or "brochure download" in subject_lower
                )

                print(
                    f"SUBJECT CHECK    : "
                    f"{'PASS ✅' if subject_pass else 'FAIL ❌'}"
                )

                # -------------------------------
                # CSV CHECK
                # -------------------------------
                csv_pass = len(csv_files) > 0

                print(
                    f"CSV CHECK        : "
                    f"{'PASS ✅' if csv_pass else 'FAIL ❌'}"
                )

                # -------------------------------
                # OVERALL
                # -------------------------------
                qualifying = (
                    date_pass
                    and sender_pass
                    and subject_pass
                    and csv_pass
                )

                if qualifying:
                    print("\n" + "🔥" * 20)
                    print("THIS EMAIL QUALIFIES FOR THE MONITOR")
                    print("🔥" * 20)
                    print("The monitor SHOULD attempt to launch")
                    print("OutlookExcelAutomation.py for this email.")
                else:
                    print("\nThis email does NOT qualify yet.")

                checked += 1

            except Exception as e:

                print(
                    f"ERROR reading email #{i}: {e}"
                )

        print("\n" + "=" * 70)
        print("DEBUG COMPLETE")
        print("=" * 70)

    except Exception as e:

        print("\n❌ OUTLOOK DEBUG FAILED")
        print(f"Error: {repr(e)}")

    finally:

        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


if __name__ == "__main__":
    main()
