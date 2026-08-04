import os
import win32com.client
import pythoncom
import pandas as pd
from datetime import datetime, timedelta
import shutil
import glob 
import subprocess
import pyautogui
import time
from Yukti_Mobile.Core.automation_engine import AutomationEngine
from Yukti_Mobile.Core.dashboard_update import update_dashboard

engine = AutomationEngine()
engine.register("Outlook Email Reader")

def update_module(module_name, status=None):
    if status:
        print(f"Updating module '{module_name}': {status}")
    else:
        print(f"Updating module '{module_name}'")

start_time = time.time()

## =====================================
# ✅ STEP 1: DATE CONTROL
# =====================================

MODE = "today"   # options: "today", "yesterday", "custom"

if MODE == "today":
    target_date = datetime.now()

elif MODE == "yesterday":
    target_date = datetime.now() - timedelta(days=1)

elif MODE == "custom":
    target_date = datetime(2026, 4, 4)   # 👈 your test date

print("Selected Date:", target_date.strftime("%d-%m-%Y"))

# =====================================
# STEP 2: CREATE FOLDER
# =====================================
base_path = r"D:\IT Pacifica\CRM\Leads Work\Year 2026 Leads"

folder_name = target_date.strftime("%d %B %Y")
export_folder = os.path.join(base_path, folder_name)

os.makedirs(export_folder, exist_ok=True)

print("Using Folder:", export_folder)


# =====================================
# STEP 3: CONNECT OUTLOOK
# =====================================
pythoncom.CoInitialize()

outlook = win32com.client.Dispatch("Outlook.Application")
namespace = outlook.GetNamespace("MAPI")
inbox = namespace.GetDefaultFolder(6)

# ✅ SAFE folder detection (no name error)
target_folder = None

for f in inbox.Folders:
    name = f.Name.strip().lower()

    if "mahek" in name and "lead" in name:
        target_folder = f
        break

if not target_folder:
    print("❌ Folder not found")
    exit()

print("Using folder:", target_folder.Name)

messages = target_folder.Items
messages.Sort("[ReceivedTime]", True)


# =====================================
# STEP 4: FILTER EMAILS (DATE + SUBJECT)
# =====================================
print("\nChecking emails...\n")

target_date_str = target_date.strftime("%d-%m-%Y")

filtered_messages = []

target_only_date = target_date.date()

for msg in messages:
    try:
        received_date = msg.ReceivedTime.date()

        # DATE FILTER
        if abs((received_date - target_only_date).days) > 0:
            continue

        # SUBJECT FILTER
        subject = str(msg.Subject).lower()

        if "lead" not in subject and "leads" not in subject:
            continue

        filtered_messages.append(msg)

    except:
        pass

print("\nTotal emails found:", len(filtered_messages))


# =====================================
# STEP 5: DOWNLOAD ATTACHMENTS
# =====================================
downloaded_files = []

for message in filtered_messages:
    try:
        attachments = message.Attachments

        for i in range(1, attachments.Count + 1):
            attachment = attachments.Item(i)
            filename = attachment.FileName

            if filename.lower().endswith(".csv"):
                save_path = os.path.join(export_folder, filename)

                if os.path.exists(save_path):
                    continue

                attachment.SaveAsFile(save_path)
                downloaded_files.append(filename)

                print("Downloaded:", filename)

    except Exception as e:
        print("Error:", e)

print("\nDownload Completed\n")

update_module(
    "Outlook Email Reader",
    status="Downloading Attachments"
)


# =====================================
# STEP 6: COPY TO RAW (OLD CRM ONLY)
# =====================================
print("Copying OLD CRM files to RAW...\n")

old_raw_folder = r"D:\Vipul Personal\CRM Automation work\Old CRM\Raw Data"
os.makedirs(old_raw_folder, exist_ok=True)

print("Cleaning OLD CRM Raw folder...")
for file in os.listdir(old_raw_folder):
    if file.endswith(".csv"):
        os.remove(os.path.join(old_raw_folder, file))

old_projects = ["casa", "north enclave", "san lucas", "san martin", "pride"]

for file in downloaded_files:

    file_lower = file.lower()

    if any(p in file_lower for p in old_projects):

        src = os.path.join(export_folder, file)
        dst = os.path.join(old_raw_folder, file)

        if not os.path.exists(dst):
            shutil.copy(src, dst)
            print("Copied:", file)

print("\nOLD CRM COPY DONE\n")


# ============================================
# STEP 7: COPY IN4 CRM FILES TO RAW
# ============================================
print("Copying IN4 CRM files to RAW...")

in4_raw_path = r"D:\Vipul Personal\CRM Automation work\In4 CRM\Raw Data"

os.makedirs(in4_raw_path, exist_ok=True)

for file in downloaded_files:

    if not file.lower().endswith(".csv"):
        continue

    file_lower = file.lower()

    # ✅ identify IN4 files (adjust if needed)
    if any(p in file_lower for p in ["amara", "enchante", "pacifica", "hillcrest"]):

        src = os.path.join(export_folder, file)
        dst = os.path.join(in4_raw_path, file)

        if not os.path.exists(dst):
            shutil.copy(src, dst)
            print("Copied (IN4):", file)

print("IN4 CRM COPY DONE\n")


# =====================================
# STEP 8: COUNT LEADS
# =====================================
print("Counting Leads...\n")

in4_projects = ["amara", "enchante", "pacifica", "hillcrest"]

old_total = 0
in4_total = 0

for file in downloaded_files:

    if not file.lower().endswith(".csv"):
        continue

    if "property" in file.lower() or "inquiry" in file.lower():
        continue

    path = os.path.join(export_folder, file)

    try:
        df = pd.read_csv(path, engine="python", encoding="utf-8", on_bad_lines="skip")
    except:
        df = pd.read_csv(path, engine="python", encoding="latin1", on_bad_lines="skip")

    df = df.dropna(how="all")

    # remove empty/garbage rows
    df = df[df.apply(lambda row: any(str(x).strip() != "" for x in row), axis=1)]

    lead_count = len(df)

    print(file, "→", lead_count, "leads")

    file_lower = file.lower()

    if any(p in file_lower for p in old_projects):
        old_total += lead_count

    elif any(p in file_lower for p in in4_projects):
        in4_total += lead_count


print("\n======================")
print("OLD CRM Leads:", old_total)
print("IN4 CRM Leads:", in4_total)
print("TOTAL:", old_total + in4_total)
print("======================")



# ==============================
# STEP 9: POWER BI AUTO REFRESH + EXPORT
# ==============================

print("Starting Power BI Automation...")

pbix_path = r"D:\Vipul Personal\CRM Automation work\Old CRM\Power BI File\Old CRM and In4 CRM Google Sheet-New .pbix"
powerbi_path = r"C:\Users\pacit\AppData\Local\Microsoft\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_8wekyb3d8bbwe\PBIDesktopStore.exe"

subprocess.Popen(f'start "" "{powerbi_path}" "{pbix_path}"', shell=True)

print("Opening correct Power BI...")
time.sleep(30)

# Refresh
print("Refreshing data...")
pyautogui.hotkey('ctrl', 'r')

time.sleep(90)   # increase if data is large

today = datetime.now()

day = today.day
month = today.strftime("%B")

# suffix (st, nd, rd, th)
if 4 <= day <= 20 or 24 <= day <= 30:
    suffix = "th"
else:
    suffix = ["st", "nd", "rd"][day % 10 - 1]

date_str = f"{day}{suffix} {month}"

file_name = f"Old CRM Automation - {date_str}.csv"

output_path = r"D:\Vipul Personal\latest Tools\Power BI\In4 CRM Leads Automation\Python Clean Output"

final_file = os.path.join(output_path,file_name)

# Export
print("Exporting file...")

pyautogui.hotkey('alt', 'f')
time.sleep(1)

pyautogui.press('e')
time.sleep(3)

# click filename box (adjust once)
pyautogui.click(600, 700)

time.sleep(1)

pyautogui.write(file_name)
time.sleep(1)

pyautogui.press('enter')

print("File saved:", file_name)

time.sleep(5)

print("Waiting for export file...")

csv_files = []

# wait up to 30 seconds for file

print("✅ File moved and renamed:", final_file)

print("File moved and renamed:", final_file)

print("Power BI Automation Done\n")

## ----------------------------------
# Dashboard Update
# ----------------------------------

elapsed = round(time.time() - start_time)

duration = f"{elapsed} sec"

engine.update_stats(
    "Outlook Email Reader",
    records=old_total + in4_total,
    success=old_total + in4_total,
    failed=0,
    duration=duration
)

engine.stop("Outlook Email Reader")

print("Updating Dashboard Summary...")

update_dashboard(
    export_folder,
    automation_name="Outlook Email Reader",
    automation_status="Completed",
    records=old_total + in4_total
)

print("Dashboard Summary Updated Successfully")
print("Dashboard Updated Successfully")

def run():
    """Placeholder run function to satisfy invocation."""
    return

if __name__ == "__main__":
    run()