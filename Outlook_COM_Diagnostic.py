import os
import sys
import platform
import socket
import getpass
import traceback
from datetime import datetime

import pythoncom
import win32com.client


# ============================================================
# OUTLOOK COM DIAGNOSTIC
# ============================================================

TARGET_FOLDER_KEYWORDS = ["mahek", "lead"]


def log(message):
    print(message, flush=True)


def main():

    log("=" * 70)
    log("OUTLOOK COM DIAGNOSTIC")
    log("=" * 70)

    # --------------------------------------------------------
    # 1. BASIC ENVIRONMENT
    # --------------------------------------------------------
    log("\n[1] ENVIRONMENT")
    log("-" * 70)

    log(f"Date/Time        : {datetime.now()}")
    log(f"Windows User     : {getpass.getuser()}")
    log(f"Computer Name    : {socket.gethostname()}")
    log(f"Python           : {sys.executable}")
    log(f"Python Version   : {sys.version}")
    log(f"Working Directory: {os.getcwd()}")
    log(f"Script Directory : {os.path.dirname(os.path.abspath(__file__))}")
    log(f"Platform         : {platform.platform()}")

    # --------------------------------------------------------
    # 2. INITIALIZE COM
    # --------------------------------------------------------
    log("\n[2] COM INITIALIZATION")
    log("-" * 70)

    pythoncom.CoInitialize()

    try:

        # ----------------------------------------------------
        # 3. CHECK OUTLOOK PROCESS
        # ----------------------------------------------------
        log("\n[3] CHECKING OUTLOOK PROCESS")
        log("-" * 70)

        try:
            import subprocess

            result = subprocess.run(
                [
                    "tasklist",
                    "/FI",
                    "IMAGENAME eq OUTLOOK.EXE"
                ],
                capture_output=True,
                text=True,
                timeout=10
            )

            log(result.stdout.strip())

            if "OUTLOOK.EXE" in result.stdout.upper():
                log("✅ Outlook.exe is running")
            else:
                log("❌ Outlook.exe is NOT running")

        except Exception as e:
            log(f"⚠ Could not check Outlook process: {e}")

        # ----------------------------------------------------
        # 4. CONNECT TO OUTLOOK
        # ----------------------------------------------------
        log("\n[4] OUTLOOK COM CONNECTION")
        log("-" * 70)

        try:
            log("Attempting:")
            log('win32com.client.Dispatch("Outlook.Application")')

            outlook = win32com.client.Dispatch("Outlook.Application")

            log("✅ Outlook.Application COM connection SUCCESSFUL")

        except Exception as e:
            log("❌ Outlook.Application COM connection FAILED")
            log(f"Error: {repr(e)}")

            traceback.print_exc()

            log("\nTHIS IS THE IMPORTANT FAILURE.")
            log("The diagnostic cannot continue without Outlook COM.")

            return

        # ----------------------------------------------------
        # 5. MAPI CONNECTION
        # ----------------------------------------------------
        log("\n[5] MAPI CONNECTION")
        log("-" * 70)

        try:
            namespace = outlook.GetNamespace("MAPI")

            log("✅ MAPI namespace obtained")

        except Exception as e:
            log("❌ MAPI connection FAILED")
            log(f"Error: {repr(e)}")
            traceback.print_exc()
            return

        # ----------------------------------------------------
        # 6. OUTLOOK VERSION
        # ----------------------------------------------------
        log("\n[6] OUTLOOK INFORMATION")
        log("-" * 70)

        try:
            log(f"Outlook Version : {outlook.Version}")
        except Exception as e:
            log(f"Could not read Outlook version: {e}")

        try:
            log(f"Outlook Object  : {outlook}")
        except Exception:
            pass

        # ----------------------------------------------------
        # 7. DEFAULT INBOX
        # ----------------------------------------------------
        log("\n[7] DEFAULT INBOX")
        log("-" * 70)

        try:
            inbox = namespace.GetDefaultFolder(6)

            log("✅ Default Inbox obtained")
            log(f"Inbox Name      : {inbox.Name}")

        except Exception as e:
            log("❌ Could not access default Inbox")
            log(f"Error: {repr(e)}")
            traceback.print_exc()
            return

        # ----------------------------------------------------
        # 8. LIST INBOX SUBFOLDERS
        # ----------------------------------------------------
        log("\n[8] INBOX SUBFOLDERS")
        log("-" * 70)

        try:

            found_folder = None

            for folder in inbox.Folders:

                folder_name = folder.Name

                log(f"Folder: {folder_name}")

                name_lower = folder_name.strip().lower()

                if all(keyword in name_lower for keyword in TARGET_FOLDER_KEYWORDS):
                    found_folder = folder

            if found_folder:

                log("\n✅ TARGET FOLDER FOUND")
                log(f"Folder Name: {found_folder.Name}")

            else:

                log("\n❌ TARGET FOLDER NOT FOUND")
                log("Looking for a folder containing:")
                log(TARGET_FOLDER_KEYWORDS)

        except Exception as e:
            log("❌ Error while reading Inbox folders")
            log(f"Error: {repr(e)}")
            traceback.print_exc()
            return

        # ----------------------------------------------------
        # 9. READ TARGET FOLDER
        # ----------------------------------------------------
        if found_folder:

            log("\n[9] TARGET FOLDER TEST")
            log("-" * 70)

            try:

                messages = found_folder.Items

                log(f"Message collection obtained")
                log(f"Total messages: {messages.Count}")

                try:
                    messages.Sort("[ReceivedTime]", True)
                    log("✅ Messages sorted by ReceivedTime")

                except Exception as e:
                    log(f"⚠ Could not sort messages: {e}")

                # ------------------------------------------------
                # 10. SHOW LATEST 10 EMAILS
                # ------------------------------------------------

                log("\n[10] LATEST EMAILS")
                log("-" * 70)

                count = min(messages.Count, 10)

                for i in range(1, count + 1):

                    try:

                        msg = messages.Item(i)

                        subject = getattr(msg, "Subject", "")
                        sender = getattr(msg, "SenderEmailAddress", "")
                        received = getattr(msg, "ReceivedTime", "")
                        unread = getattr(msg, "UnRead", "")

                        log(
                            f"\nEmail #{i}\n"
                            f"  Subject : {subject}\n"
                            f"  Sender  : {sender}\n"
                            f"  Received: {received}\n"
                            f"  Unread  : {unread}"
                        )

                    except Exception as e:

                        log(f"⚠ Could not read email #{i}: {e}")

            except Exception as e:

                log("❌ Could not read target folder messages")
                log(f"Error: {repr(e)}")
                traceback.print_exc()

        # ----------------------------------------------------
        # 11. FINAL RESULT
        # ----------------------------------------------------
        log("\n" + "=" * 70)
        log("DIAGNOSTIC COMPLETE")
        log("=" * 70)

        log("\nIf everything above shows ✅:")
        log("Outlook COM itself is working in this execution environment.")

        log("\nIf VS Code works but Task Scheduler fails:")
        log("the difference is specifically the Task Scheduler environment.")

    finally:

        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


if __name__ == "__main__":
    main()                                                                                              