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

def clean_and_map_data(df):
    # 1. Standardize all headers
    df.columns = [str(c).lower().replace("_", " ").strip() for c in df.columns]
    
    # 2. FORCE SYNC: Move data from any raw header to our standard headers
    for col in df.columns:
        if any(x in col for x in ['mobile', 'phone', 'contact']): df['Mobile Number'] = df[col]
        if any(x in col for x in ['project', 'property', 'page', 'campaign', 'form name']): df['Project Name'] = df[col]
        if any(x in col for x in ['email', 'mail']): df['Email ID'] = df[col]
        if any(x in col for x in ['source', 'platform']): df['src_raw'] = df[col]
        if any(x in col for x in ['full name', 'name']): df['name_raw'] = df[col]

    # 3. Clean Name (ASCII only)
    if 'name_raw' in df.columns:
        df['name_raw'] = df['name_raw'].astype(str).apply(lambda x: re.sub(r'[^a-zA-Z\s]', '', x).strip())
        df[['First Name', 'Last Name']] = df['name_raw'].str.split(' ', n=1, expand=True)
        df['Last Name'] = df['Last Name'].fillna('')
    else:
        df['First Name'], df['Last Name'] = "", ""

    # 4. Clean Mobile
    if 'Mobile Number' in df.columns:
        cl = df['Mobile Number'].astype(str).str.replace('P:', '', case=False).str.replace('+91', '').replace(r'\D', '', regex=True)
        df['Mobile Number'] = pd.to_numeric(cl, errors='coerce')

    # 5. THE HYBRID MAPPER (Custom for you + Universal for others)
    # This checks for your keywords first. If found, it maps them. 
    # If NOT found, it cleans the text professionally.
    proj_map = {'hillcrest': 'PIHCP2', 'amara': 'AP', 'enchante': 'EC', 'pacifica one': 'HB'}
    
    if 'Project Name' in df.columns:
        def hybrid_mapper(val):
            v_lower = str(val).lower()
            # A. Check for your custom company codes
            for keyword, code in proj_map.items():
                if keyword in v_lower:
                    return code
            
            # B. Universal Logic: Clean noise words for global clients
            noise = ['lead', 'gen', 'campaign', 'new', 'copy', 'july', 'june']
            clean_v = v_lower
            for word in noise:
                clean_v = clean_v.split(word)[0]
            return clean_v.strip().title()
            
        df['Project Name'] = df['Project Name'].apply(hybrid_mapper)

    # 6. Source Mapping
    src_map = {'ig': 'Instagram', 'fb': 'Facebook', 'an': 'Facebook', 'fc': 'Facebook'}
    if 'src_raw' in df.columns:
        df['Source of Information'] = df['src_raw'].astype(str).str.lower().str.strip().map(src_map).fillna(df['src_raw'].astype(str).str.title())

    # 7. Final Ordered Sequence
    cols = ['First Name', 'Last Name', 'Email ID', 'Mobile Number', 'Source of Information', 'Project Name']
    for c in cols: 
        if c not in df.columns: df[c] = ""
        
    return df[cols]

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

                    try:

                        df = pd.read_csv(
                            file,
                            encoding="latin1"
                        )

                    except:

                        df = pd.read_csv(
                            file,
                            encoding="latin1",
                            sep=None,
                            engine="python",
                            on_bad_lines="skip"
                        )

                else:

                    df = pd.read_excel(file)

                all_dfs.append(df)

                log_debug(
                    f"Loaded : {os.path.basename(file)}"
                )

            except Exception as e:

                log_debug(
                    f"Skipped : {os.path.basename(file)} | {e}"
                )

        if len(all_dfs) == 0:

            return 0, None

        final_df = clean_and_map_data(

            pd.concat(
                all_dfs,
                ignore_index=True
            )

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

            fmt = writer.book.add_format(

                {"num_format": "0"}

            )

            idx = final_df.columns.get_loc(

                "Mobile Number"

            )

            writer.sheets["Leads"].set_column(

                idx,

                idx,

                18,

                fmt

            )

        writer.close()

        log_debug(

            f"{crm_name} Master Created"

        )

        return len(final_df), outfile
    
    
    # -------------------------------------------------------
    # Process OLD CRM
    # -------------------------------------------------------
    old_count, old_file = process_folder(OLDCRM_RAW, "OldCRM")
    if old_file:
        attachments.append(old_file)
    summary.append(f"Old CRM : {old_count}")

    # -------------------------------------------------------
    # Process IN4 CRM
    # -------------------------------------------------------
    in4_count, in4_file = process_folder(IN4CRM_RAW, "In4CRM")
    if in4_file:
        attachments.append(in4_file)
    summary.append(f"In4 CRM : {in4_count}")

    total = old_count + in4_count

    body = f"""Yukti-AI Daily CRM Automation Report

Old CRM Leads : {old_count}
In4 CRM Leads : {in4_count}

------------------------------------

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
    