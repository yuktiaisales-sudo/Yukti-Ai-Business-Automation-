import json
import os
import pythoncom
import win32com.client
from datetime import datetime

FOLDER_KEYWORDS = ["mahek", "lead"]
SENDER = "mchopra@pacificacompanies.in"
PROCESSED_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "processed_marketing_emails.json"
)

def get_sender(message):
    try:
        return str(getattr(message, "SenderEmailAddress", "")).strip().lower()
    except Exception:
        return ""

def main():
    print("=" * 70)
    print("YUKTI-AI - COMPARE OUTLOOK ENTRY IDs")
    print("=" * 70)

    try:
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            processed = set(json.load(f))
    except Exception as e:
        print("Could not read processed file:", e)
        return

    print(f"Stored processed IDs: {len(processed)}")

    pythoncom.CoInitialize()

    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        inbox = namespace.GetDefaultFolder(6)

        target = None
        for folder in inbox.Folders:
            name = folder.Name.strip().lower()
            if "mahek" in name and "lead" in name:
                target = folder
                break

        if target is None:
            print("❌ Mahek Chopra - Leads folder not found.")
            return

        messages = target.Items
        messages.Sort("[ReceivedTime]", True)

        print(f"Folder: {target.Name}")
        print(f"Total messages: {messages.Count}")

        print("\nToday's qualifying emails:")
        print("=" * 70)

        count = 0

        for i in range(1, messages.Count + 1):
            if count >= 10:
                break

            msg = messages.Item(i)

            try:
                received = msg.ReceivedTime
                if received.date() != datetime.now().date():
                    continue

                sender = get_sender(msg)
                subject = str(getattr(msg, "Subject", "")).strip()
                subject_lower = subject.lower()

                if sender != SENDER:
                    continue

                if (
                    "lead" not in subject_lower
                    and "brochure download" not in subject_lower
                ):
                    continue

                csv_found = False
                attachments = msg.Attachments
                for j in range(1, attachments.Count + 1):
                    filename = str(
                        attachments.Item(j).FileName
                    ).strip().lower()
                    if filename.endswith(".csv"):
                        csv_found = True
                        break

                if not csv_found:
                    continue

                entry_id = str(msg.EntryID)

                print(f"\nEMAIL #{count + 1}")
                print(f"Subject          : {subject}")
                print(f"Received         : {received}")
                print(f"EntryID          : {entry_id}")
                print(
                    "Already processed: "
                    + ("YES ❌" if entry_id in processed else "NO ✅")
                )

                count += 1

            except Exception as e:
                print(f"Error reading item #{i}: {e}")

        print("\n" + "=" * 70)
        print("RESULT")
        print("=" * 70)

        if count == 0:
            print("No qualifying emails found today.")
        else:
            print(f"Qualifying emails found: {count}")
            print(
                "If any email says 'Already processed: YES ❌', "
                "that email will be skipped by the monitor."
            )
            print(
                "If an email says 'Already processed: NO ✅', "
                "the monitor should continue to the launch check."
            )

    finally:
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass

if __name__ == "__main__":
    main()
