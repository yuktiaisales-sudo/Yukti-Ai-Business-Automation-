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

    log_debug("--- AUTOMATION STARTED ---")

    # =====================================================
    # PRODUCTION PATHS
    # =====================================================

    OLDCRM_RAW = r"D:\Vipul Personal\CRM Automation work\Old CRM\Raw Data"

    IN4CRM_RAW = r"D:\Vipul Personal\CRM Automation work\In4 CRM\Raw Data"

    MASTER_FOLDER = r"D:\Vipul Personal\CRM Automation work\Master Files"

    os.makedirs(MASTER_FOLDER, exist_ok=True)

    files = []
    cfg = load_config()

    # ------------------------
    # OLD CRM
    # ------------------------
    if os.path.exists(OLDCRM_RAW):

        files.extend([
            os.path.join(OLDCRM_RAW, f)
            for f in os.listdir(OLDCRM_RAW)
            if f.lower().endswith((".xlsx", ".csv"))
        ])

    # ------------------------
    # IN4 CRM
    # ------------------------
    if os.path.exists(IN4CRM_RAW):

        files.extend([
            os.path.join(IN4CRM_RAW, f)
            for f in os.listdir(IN4CRM_RAW)
            if f.lower().endswith((".xlsx", ".csv"))
        ])

    if not files:
        log_debug("No input files found in source directories.")
        return "No input files found."

    out_f = os.path.join(MASTER_FOLDER, f"Master_Report_{datetime.now().strftime('%Y%m%d')}.xlsx")

    all_dfs = []
    
    for f in files:
     cd..print(f)

    for f in files:
        try:
            if f.lower().endswith(".csv"):
                try:
                    df = pd.read_csv(f, encoding="latin1")
                except:
                    df = pd.read_csv(
                        f,
                        encoding="latin1",
                        sep=None,
                        engine="python"
                    )
            else:
                df = pd.read_excel(f)

            all_dfs.append(df)
            log_debug(f"Loaded : {os.path.basename(f)}")

        except Exception as e:
            log_debug(f"Skipped {os.path.basename(f)} : {e}")

    final_df = clean_and_map_data(pd.concat(all_dfs, ignore_index=True))

    writer = pd.ExcelWriter(out_f, engine='xlsxwriter')
    final_df.to_excel(writer, index=False, sheet_name='Leads')
    if 'Mobile Number' in final_df.columns:
        fmt = writer.book.add_format({'num_format': '0'})
        writer.sheets['Leads'].set_column(final_df.columns.get_loc('Mobile Number'), final_df.columns.get_loc('Mobile Number'), 18, fmt)
    writer.close()

    try:
        with open(os.path.join(APP_DIR, "license.json"), 'r') as f:
            comp = json.load(f).get('customer', {}).get('comp', 'Client')
    except:
        comp = "Client"

    success = send_email_automated(cfg, f"{comp} CRM Report", "Master Sheet Processed Successfully.", [out_f])
    return f"Success: {len(final_df)} leads processed."

if __name__ == "__main__":

    if "--silent" in sys.argv:
        start_process()

    else:
        start_process()