import encodings
from importlib.metadata import files
import os, pandas as pd, re, json, ssl, smtplib, sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import re

APP_DIR = os.path.join(os.environ.get('APPDATA', 'C:'), "YuktiAI")
CONFIG_FILENAME = "yukti_compact_config.json"

def log_debug(msg):
    try:
        os.makedirs(APP_DIR, exist_ok=True)
        with open(os.path.join(APP_DIR, "debug_log.txt"), "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except: pass

def load_config():
    paths = [CONFIG_FILENAME, os.path.join(APP_DIR, CONFIG_FILENAME)]
    for p in paths:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                d = json.load(f)
                return {k: (v.strip() if isinstance(v, str) else v) for k, v in d.items()}
    return None

def clean_and_map_data(df, crm_name="Old CRM"):

    import pandas as pd
    import re

    # ---------------------------------
    # Standardize Column Names
    # ---------------------------------

    df.columns = [
        str(c).strip().lower().replace("_", " ")
        for c in df.columns
    ]

    mobile_col = None
    email_col = None
    project_col = None
    source_col = None
    name_col = None

    for c in df.columns:

        c = c.strip().lower()

        # ---------------- Mobile ----------------

        if mobile_col is None and any(x in c for x in [
            "mobile",
            "phone",
            "phone number",
            "phone_number",
            "contact"
        ]):
            mobile_col = c

        # ---------------- Email ----------------

        elif email_col is None and any(x in c for x in [
            "email",
            "email id",
            "email_id",
            "mail"
        ]):
            email_col = c

        # ---------------- Project ----------------

        elif project_col is None and any(x in c for x in [
            "project",
            "property",
            "campaign",
            "campaign name",
            "campaign_name",
            "form name",
            "form_name",
            "page"
        ]):
            project_col = c

        # ---------------- Source ----------------

        elif source_col is None and any(x in c for x in [
            "source",
            "platform",
            "lead source"
        ]):
            source_col = c

        # ---------------- Name ----------------

        elif name_col is None and any(x in c for x in [
            "full name",
            "full_name",
            "name",
            "lead name"
        ]):
            name_col = c

    print("="*80)
    print("Detected Columns")
    print("Name    :", name_col)
    print("Mobile  :", mobile_col)
    print("Email   :", email_col)
    print("Project :", project_col)
    print("Source  :", source_col)
    print("="*80)
    
    if project_col:
        print(df[project_col].head(10).tolist())

    if name_col:
        print(df[name_col].head(10).tolist())
    # -------------------------------
    # Create NEW Master DataFrame
    # -------------------------------

    master = pd.DataFrame(index=df.index)

    # -------------------------------
    # Name
    # -------------------------------

    if name_col:

        names = (
            df[name_col]
            .fillna("")
            .astype(str)
            .apply(lambda x: re.sub(r'[^A-Za-z ]', '', x).strip())
        )

        split = names.str.split(" ", n=1, expand=True)

        master["First Name"] = split[0].fillna("")

        if split.shape[1] > 1:
            master["Last Name"] = split[1].fillna("")
        else:
            master["Last Name"] = ""

    else:

        master["First Name"] = ""

        master["Last Name"] = ""

    # -------------------------------
    # Email
    # -------------------------------

    if email_col:

        master["Email ID"] = (
            df["email"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
      
    )   
  
    # -------------------------------
    # Mobile
    # -------------------------------

    if mobile_col:

        master["Mobile Number"] = (
            df["phone_number"]
            .fillna("")
            .astype(str)
            .str.replace(r"\D", "", regex=True)
            .str[-10:]
        )

    # -------------------------------
    # Project
    # -------------------------------

    if project_col:
        
        p = df[project_col].fillna("").astype(str).str.lower()

        def map_project_old(x):

            x = str(x).lower()

            if "north enclave" in x:
                return "North Enclave"

            if "san lucas" in x:
                return "San Lucas"

            if "san martin" in x:
                return "San Martin"

            if "casa" in x:
                return "Casa Lakeside"

            if "pride" in x:
                return "Pride Towers"

    def map_project_in4(x):

        x = str(x).lower()

        if "hillcrest" in x:
            return "PIHCP2"

        if "enchante" in x:
            return "EC"

        if "pacifica one" in x:
            return "HB"

        if "amara" in x:
            return "AP"

        return ""
    if crm_name == "Old CRM":
        master["Project Name"] = p.apply(map_project_old)
    else:
        master["Project Name"] = p.apply(map_project_in4)
    # -------------------------------
    # Source
    # -------------------------------

    if source_col:

        s = df[source_col].fillna("").astype(str).str.lower()

        src = (
            df["platform"]
            .fillna("")
            .astype(str)
            .str.title()
)

    master["Source of Information"] = src           
            

    # -------------------------------
    # Remove completely blank rows
    # -------------------------------

    master = master.fillna("")

    # Remove only rows where ALL columns are blank
    master = master[
        ~(
            (master["First Name"] == "") &
            (master["Last Name"] == "") &
            (master["Email ID"] == "") &
            (master["Mobile Number"] == "") &
            (master["Project Name"] == "") &
            (master["Source of Information"] == "")
        )
    ]

    master.reset_index(drop=True, inplace=True)

    return master

def send_email_automated(cfg, subject, body, attachments=None, recipient=None):
    try:
        sender = cfg.get('smtp_email', '').strip()
        final_recipient = str(recipient).strip() if (recipient and recipient != True) else cfg.get('to_emails', '').strip()
        msg = MIMEMultipart()
        msg["From"] = f"{cfg.get('display_name', 'Yukti')} <{sender}>"
        msg["To"] = final_recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html" if "<" in body else "plain"))
        for f in attachments or []:
            if os.path.exists(f):
                with open(f, "rb") as att:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(att.read())
                    encoders.encode_base64(part); part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(f)}")
                    msg.attach(part)
        port = int(cfg.get('smtp_port', 587))
        server_addr = cfg.get('smtp_server', '').strip()
        server = smtplib.SMTP_SSL(server_addr, port, timeout=25) if port == 465 else smtplib.SMTP(server_addr, port, timeout=25)
        if port != 465:
            server.ehlo()
            if server.has_extn("STARTTLS"): server.starttls(context=ssl.create_default_context()); server.ehlo()
        server.login(sender, cfg['smtp_password'].replace(" ", "").strip())
        server.sendmail(sender, [final_recipient], msg.as_string()); server.quit()
        return True
    except Exception as e:
        log_debug(f"SMTP Error: {e}"); return False

def start_process():

    log_debug("========== YUKTI-AI AUTOMATION STARTED ==========")

    cfg = load_config()

    if not cfg:
        return "Configuration file not found."

    # -------------------------------------------------------
    # Production Folders
    # -------------------------------------------------------

    OLDCRM_RAW = r"D:\Vipul Personal\CRM Automation work\Old CRM\Raw Data"

    IN4CRM_RAW = r"D:\Vipul Personal\CRM Automation work\In4 CRM\Raw Data"

    MASTER_FOLDER = r"D:\Vipul Personal\CRM Automation work\Master Files"

    os.makedirs(MASTER_FOLDER, exist_ok=True)

    attachments = []

    summary = []

    def process_folder(folder_path, crm_name):

        log_debug(f"Starting {crm_name}")

        files = []

        if os.path.exists(folder_path):

            files = [

                os.path.join(folder_path, f)

                for f in os.listdir(folder_path)

                if f.lower().endswith((".csv", ".xlsx", ".xls"))

            ]

        if len(files) == 0:

            log_debug(f"No files found for {crm_name}")

            return 0, None

        all_dfs = []

        for file in files:
            try:
                if file.lower().endswith(".csv"):
                    encodings = ["utf-8", "utf-16", "utf-16le", "utf-16be", "latin1"]

                    df = None

                    for enc in encodings:
                        try:
                            df = pd.read_csv(
                                file,
                                encoding=enc,
                                sep=None,
                                engine="python",
                                on_bad_lines="skip"
                            )
                            print(f"{os.path.basename(file)} --> {enc}")
                            break
                        except Exception:
                            pass

                    if df is None:
                        print(f"Cannot read {file}")
                        continue

                    # Same cleaning as CRM_Automationw1.py
                    df = df.dropna(how="all")
                    df = df[df.apply(lambda row: any(str(x).strip() != "" for x in row), axis=1)]

                else:
                    df = pd.read_excel(file)
                    df = df.dropna(how="all")

                print(f"{os.path.basename(file)} : {len(df)} rows")

                # Clean each file individually
                clean_df = clean_and_map_data(df)

                if len(clean_df) > 0:
                    all_dfs.append(clean_df)

            except Exception as e:
                print(f"ERROR : {file}")
                print(e)
                log_debug(f"Skipped : {os.path.basename(file)} | {e}")

        if len(all_dfs) == 0:

            return 0, None
        print("\nColumns found:")
        print(all_dfs[0].columns.tolist())

        final_df = pd.concat(
    all_dfs,
    ignore_index=True
)
        
        outfile = os.path.join(
            MASTER_FOLDER,
            f"{crm_name}_Master_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )

        writer = pd.ExcelWriter(
            outfile,
            engine="xlsxwriter"
        )

        final_df.to_excel(
            writer,
            sheet_name="Leads",
            index=False
        )

        if "Mobile Number" in final_df.columns:
            fmt = writer.book.add_format({"num_format": "0"})
            idx = final_df.columns.get_loc("Mobile Number")
            writer.sheets["Leads"].set_column(idx, idx, 18, fmt)

        writer.close()
        log_debug(f"{crm_name} Master Created")
        return len(final_df), outfile
    
        print("Saved:", outfile)
        print("Rows written:", len(final_df))


    old_count, old_file = process_folder(OLDCRM_RAW, "OldCRM")
    in4_count, in4_file = process_folder(IN4CRM_RAW, "In4CRM")

    attachments = [f for f in [old_file, in4_file] if f]
    total = old_count + in4_count

    body = f"""
Total Leads : {total}

Both Master Sheets are attached.
"""

    send_email_automated(cfg,
                         "Yukti-AI Daily CRM Report",
                         body,
                         attachments)

    log_debug("Automation Completed Successfully")

    return f"""Old CRM : {old_count}
In4 CRM : {in4_count}
Total : {total}
"""


if __name__ == "__main__":
    result = start_process()
    print(result)
    