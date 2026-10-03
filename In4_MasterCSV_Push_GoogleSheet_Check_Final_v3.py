import os
import re
import json
import time
import smtplib
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("In4_MasterCSV_Push")


# =====================================================
# IN4 CRM API CONFIG
# =====================================================

API_USER = "PacificaApiuser"
API_KEY = "Pacifica@123"

TOKEN_URL = "https://pacerppacificacompanies.in/SalesLeadService/api/Lead/GetSecurityToken"

CREATE_LEAD_URL = "https://pacerppacificacompanies.in/SalesLeadService/api/Lead/CreateSalesLead"

# =====================================================
# SMTP EMAIL CONFIGURATION
# =====================================================

SMTP_SERVER = "pacificacompanies.icewarpcloud.in"
SMTP_PORT = 587

SMTP_EMAIL = "test@pacificacompanies.in"
SMTP_PASSWORD = "Autoemail@#123"

SUMMARY_TO = "vshah@pacificacompanies.in"


# ============================================================
# MASTER CSV INPUT FOLDER
# ============================================================

INPUT_FOLDER = Path(
    r"D:\Vipul Personal\CRM Automation work\In4 CRM\IN4 Input"
)

# ============================================================
# MASTER CSV DATE MODE
# ============================================================
#
# AUTO   = automatically use today's Master CSV.
# CUSTOM = use the exact date entered below.
#
# Date format for CUSTOM:
# YYYY-MM-DD
#
# Example:
# MASTER_CSV_MODE = "CUSTOM"
# CUSTOM_MASTER_DATE = "2026-09-22"
#
MASTER_CSV_MODE = "Custom"
CUSTOM_MASTER_DATE = "2026-09-23"


# ============================================================
# GOOGLE SHEET DUPLICATE CHECK CONFIG
# ============================================================

# Paste the SAME Google Sheet URL used by the morning
# Google Sheet -> In4 CRM automation here.
GOOGLE_SHEET_URL = ""

CREDENTIALS_FILE = r"D:\Vipul Personal\Power BI CRM Leads Automation Project\AI Buddy BKP\credentials.json"

SPREADSHEET_NAME = "Leads Mastersheet"

GOOGLE_PROJECT_SHEETS = [
    "Amara",
    "Hillcrest",
    "Pacifica One",
    "Enchante"
]

# Only these statuses mean that the Google Sheet lead has
# already reached / been confirmed by In4 CRM.
GOOGLE_CONFIRMED_STATUSES = {
    "uploaded",
    "duplicate"
}


# ============================================================
# PROJECT MAPPING
# ============================================================

PROJECT_SHEETS = [
    "Amara",
    "Hillcrest",
    "Pacifica One",
    "Enchante"
    ]

# =====================================================
# PROJECT MAPPING
# =====================================================

PROJECT_MAPPING = {
    "AP": "AMARA",
    "PIHCP2": "HILLCREST PHASE 2",
    "HB": "PACIFICA ONE",
    "EC": "ENCHANTE",

    # Upcoming projects:
    # These are available for Master CSV -> In4 CRM push.
    # They are intentionally NOT added to the Google Sheet comparison
    # list yet because they are not present in the Google Sheet today.
    "AVPH3": "AVPH3",
    "PCBT": "PCBT",

    # Also accept full project names if they appear in the Master CSV.
    "AURUM VILLAS PHASE-3": "AVPH3",
    "BLISS TOWER": "PCBT"
}

# ============================================================
# EXPECTED MASTER CSV COLUMNS
# ============================================================


REQUIRED_COLUMNS = [
    "In4 CRM CSV Final[First Name]",
    "In4 CRM CSV Final[Last Name]",
    "In4 CRM CSV Final[Preferred Contact Number]",
    "In4 CRM CSV Final[Source Of Information]",
    "In4 CRM CSV Final[Email Id]",
    "In4 CRM CSV Final[Project Code]"
]



# ============================================================
# EMAIL REPORT FUNCTION
# ============================================================

def send_report(
    csv_file,
    total_count,
    uploaded_count,
    duplicate_count,
    failed_count,
    invalid_mobile_count,
    token_failed_count,
    project_stats,
    source_stats,
    failed_leads,
    google_sheet_match_count=0,
    new_lead_candidate_count=0
):

    subject = "Daily IN4CRM Lead Upload Automation Report"

    generated_time = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )

    # --------------------------------------------------------
    # PROJECT SUMMARY
    # --------------------------------------------------------

    project_rows = ""

    for project, count in sorted(project_stats.items()):

        project_rows += f"""
        <tr>
            <td>{project}</td>
            <td>{count}</td>
        </tr>
        """

    # --------------------------------------------------------
    # SOURCE SUMMARY
    # --------------------------------------------------------

    source_rows = ""

    for source, count in sorted(source_stats.items()):

        source_rows += f"""
        <tr>
            <td>{source}</td>
            <td>{count}</td>
        </tr>
        """

    # --------------------------------------------------------
    # FAILED LEADS
    # --------------------------------------------------------

    failed_rows = ""

    for item in failed_leads:

        failed_rows += f"""
        <tr>
            <td>{item.get("first_name", "")}</td>
            <td>{item.get("last_name", "")}</td>
            <td>{item.get("mobile", "")}</td>
            <td>{item.get("email", "")}</td>
            <td>{item.get("project", "")}</td>
            <td>{item.get("reason", "")}</td>
        </tr>
        """

    if not failed_rows:
        failed_rows = """
        <tr>
            <td colspan="6">No failed leads</td>
        </tr>
        """

    # --------------------------------------------------------
    # HTML EMAIL
    # --------------------------------------------------------

    body = f"""
    <html>

    <head>

    <style>

    body {{
        font-family: Segoe UI, Arial, sans-serif;
        background: #f4f6f8;
        color: #222;
    }}

    h2 {{
        color: #1558d6;
    }}

    table {{
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 20px;
        background: white;
    }}

    th {{
        background: #1558d6;
        color: white;
        padding: 8px;
        text-align: left;
    }}

    td {{
        border: 1px solid #ddd;
        padding: 8px;
    }}

    .summary {{
        font-size: 16px;
        font-weight: bold;
    }}

    </style>

    </head>

    <body>

    <h2>IN4 CRM Daily Lead Upload Report</h2>

    <p>
        <b>File:</b> {csv_file.name}<br>
        <b>Report Time:</b> {generated_time}
    </p>

    <table>

        <tr>
            <th>Total Leads</th>
            <th>Uploaded</th>
            <th>Duplicate</th>
            <th>Failed</th>
            <th>Invalid Mobile</th>
            <th>Token Failed</th>
        </tr>

        <tr>
            <td>{total_count}</td>
            <td>{uploaded_count}</td>
            <td>{duplicate_count}</td>
            <td>{failed_count}</td>
            <td>{invalid_mobile_count}</td>
            <td>{token_failed_count}</td>
        </tr>

    </table>


    <h3>Google Sheet Duplicate Check</h3>

    <table>
        <tr>
            <th>Master CSV Leads</th>
            <th>Found in Google Sheet</th>
            <th>New Leads for CRM Check</th>
        </tr>
        <tr>
            <td>{total_count}</td>
            <td>{google_sheet_match_count}</td>
            <td>{new_lead_candidate_count}</td>
        </tr>
    </table>

    <h3>Project-wise Summary</h3>

    <table>

        <tr>
            <th>Project</th>
            <th>Leads Uploaded</th>
        </tr>

        {project_rows}

    </table>


    <h3>Source-wise Summary</h3>

    <table>

        <tr>
            <th>Source</th>
            <th>Leads Uploaded</th>
        </tr>

        {source_rows}

    </table>


    <h3>Failed / Invalid Leads</h3>

    <table>

        <tr>
            <th>First Name</th>
            <th>Last Name</th>
            <th>Mobile</th>
            <th>Email</th>
            <th>Project</th>
            <th>Reason</th>
        </tr>

        {failed_rows}

    </table>


    <p>
        <b>IN4 Master CSV Automation completed.</b>
    </p>

    </body>

    </html>
    """

    msg = MIMEMultipart()

    msg["From"] = SMTP_EMAIL
    msg["To"] = SUMMARY_TO
    msg["Subject"] = subject

    msg.attach(
        MIMEText(body, "html")
    )

    try:

        server = smtplib.SMTP(
            SMTP_SERVER,
            SMTP_PORT,
            timeout=30
        )

        "server.starttls()"

        server.login(
            SMTP_EMAIL,
            SMTP_PASSWORD
        )

        server.sendmail(
            SMTP_EMAIL,
            SUMMARY_TO,
            msg.as_string()
        )

        server.quit()

        logger.info(
            "Summary email sent successfully to %s",
            SUMMARY_TO
        )

    except Exception as e:

        logger.error(
            "Failed to send summary email: %s",
            e
        )


# ============================================================
# FIND MASTER CSV
# ============================================================

def find_master_csv():

    INPUT_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    pattern = "In4 CRM  - CSV-*.csv"

    files = list(
        INPUT_FOLDER.glob(pattern)
    )

    if not files:

        logger.warning(
            "No Master CSV found in: %s",
            INPUT_FOLDER
        )

        return None

    # --------------------------------------------------------
    # CUSTOM MODE
    # --------------------------------------------------------

    if MASTER_CSV_MODE.strip().upper() == "CUSTOM":

        try:
            custom_date = datetime.strptime(
                CUSTOM_MASTER_DATE.strip(),
                "%Y-%m-%d"
            )

        except ValueError:

            print(
                "ERROR: CUSTOM_MASTER_DATE must be YYYY-MM-DD"
            )

            return None

        custom_filename = (
            f"In4 CRM  - CSV-"
            f"{custom_date.strftime('%Y-%m-%d')}.csv"
        )

        custom_file = INPUT_FOLDER / custom_filename

        if custom_file.exists():

            print(
                f"Custom Master CSV selected: "
                f"{custom_file.name}"
            )

            return custom_file

        print(
            f"Custom Master CSV not found: "
            f"{custom_file.name}"
        )

        return None

    # --------------------------------------------------------
    # AUTO MODE - TODAY'S FILE
    # --------------------------------------------------------

    today_string = datetime.now().strftime("%Y-%m-%d")

    today_file = (
        INPUT_FOLDER /
        f"In4 CRM  - CSV-{today_string}.csv"
    )

    if today_file.exists():

        logger.warning(
            "Today's Master CSV found: %s",
            today_file
        )

        return today_file

    # --------------------------------------------------------
    # AUTO MODE - FALLBACK TO LATEST CSV
    # --------------------------------------------------------

    files.sort(
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )

    logger.warning(
        "Today's CSV not found. Using latest CSV: %s",
        files[0]
    )

    return files[0]


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(value):

    if value is None:
        return ""

    if pd.isna(value):
        return ""

    return str(value).strip()


# ============================================================
# EMAIL VALIDATION
# ============================================================

def is_valid_email(email):
    email = clean_text(email)

    if not email:
        return False

    return bool(
        re.match(
            r"^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$",
            email
        )
    )


# ============================================================
# MOBILE CLEANING
# ============================================================

def clean_mobile(mobile):

    mobile = clean_text(mobile)

    # Remove P: / p:
    mobile = mobile.replace("P:", "")
    mobile = mobile.replace("p:", "")

    # Remove +91
    mobile = mobile.replace("+91", "")

    # Remove spaces
    mobile = mobile.replace(" ", "")

    # Remove hyphen
    mobile = mobile.replace("-", "")

    # Keep only numeric characters
    mobile = re.sub(
        r"\D",
        "",
        mobile
    )

    # Remove leading zero
    if mobile.startswith("0"):
        mobile = mobile[1:]

    return mobile


# ============================================================
# LOAD CONFIRMED MOBILES FROM GOOGLE SHEET
# ============================================================

def get_google_sheet_confirmed_mobiles():

    confirmed_mobiles = set()

    try:

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE,
            scope
        )

        client = gspread.authorize(credentials)

        if GOOGLE_SHEET_URL.strip():
            spreadsheet = client.open_by_url(
                GOOGLE_SHEET_URL.strip()
            )
        else:
            spreadsheet = client.open(
                SPREADSHEET_NAME
            )

        total_rows = 0

        for sheet_name in GOOGLE_PROJECT_SHEETS:

            logger.info(
                "Reading Google Sheet tab: %s",
                sheet_name
            )

            try:
                worksheet = spreadsheet.worksheet(sheet_name)
            except Exception as e:
                logger.error(
                    "Google Sheet tab not found: %s | %s",
                    sheet_name,
                    e
                )
                return {
                    "success": False,
                    "mobiles": set(),
                    "message": f"Google Sheet tab not found: {sheet_name}"
                }

            data = worksheet.get_all_records()
            total_rows += len(data)

            for row in data:

                status = clean_text(
                    row.get("upload_status", "")
                ).lower()

                if status not in GOOGLE_CONFIRMED_STATUSES:
                    continue

                mobile = clean_mobile(
                    row.get("phone_number", "")
                )

                if mobile and len(mobile) >= 10:
                    confirmed_mobiles.add(mobile)

        logger.info(
            "Google Sheet rows read: %s",
            total_rows
        )

        logger.info(
            "Confirmed Google Sheet mobiles: %s",
            len(confirmed_mobiles)
        )

        return {
            "success": True,
            "mobiles": confirmed_mobiles,
            "message": "Google Sheet duplicate list loaded"
        }

    except Exception as e:

        logger.error(
            "Google Sheet duplicate check failed: %s",
            e
        )

        return {
            "success": False,
            "mobiles": set(),
            "message": str(e)
        }


# ============================================================
# PROJECT MAPPING
# ============================================================

def map_project(project_name):

    project_name = clean_text(
        project_name
    )

    # Exact project name
    if project_name in PROJECT_MAPPING:

        return PROJECT_MAPPING[
            project_name
        ]

    # Already mapped code
    if project_name in PROJECT_MAPPING.values():

        return project_name

    # Case-insensitive matching
    for name, code in PROJECT_MAPPING.items():

        if name.lower() == project_name.lower():

            return code

    # If unknown, preserve original value
    return project_name


# ============================================================
# SOURCE MAPPING
# ============================================================

def map_source(source):

    source = clean_text(
        source
    ).lower()

    # Instagram
    if (
        "instagram" in source
        or source == "ig"
    ):

        return "Instagram", 1044

    # Facebook
    elif (
        "facebook" in source
        or source in ["fb", "an"]
    ):

        return "Facebook", 1040

    # Other
    else:

        if source:

            source_name = source.title()

        else:

            source_name = "Facebook"

        return source_name, 15


# ============================================================
# GET SECURITY TOKEN
# ============================================================

def get_security_token():

    params = {
        "apiuser": API_USER,
        "apiKey": API_KEY
    }

    try:

        token_response = requests.get(
            TOKEN_URL,
            params=params,
            timeout=30
        )

        logger.info(
            "Token API Status: %s",
            token_response.status_code
        )

        token_data = token_response.json()

        token_id = token_data.get(
            "tokenId"
        )

        if not token_id:

            logger.error(
                "Token not returned by API: %s",
                token_data
            )

            return None

        return token_id

    except Exception as e:

        logger.error(
            "Token API Error: %s",
            e
        )

        return None


# ============================================================
# PUSH ONE LEAD TO IN4 CRM
# ============================================================

def PUSH_TO_IN4_CRM(lead):

    token_id = get_security_token()

    if not token_id:

        return {
            "status": "token_failed",
            "message": "Security token failed"
        }


    # ============================================================
    # EXTRACT DATA FROM IN4 MASTER CSV
    # ============================================================

    first_name = clean_text(
        lead.get("In4 CRM CSV Final[First Name]")
    )

    last_name = clean_text(
        lead.get("In4 CRM CSV Final[Last Name]")
    )

    email = clean_text(
        lead.get("In4 CRM CSV Final[Email Id]")
    )

    mobile = clean_mobile(
        lead.get("In4 CRM CSV Final[Preferred Contact Number]")
    )

    email_valid = is_valid_email(email)
    mobile_valid = bool(mobile) and len(mobile) >= 10

    # If mobile is invalid but email is valid, still allow the
    # lead to be sent to CRM. The invalid mobile is sent as blank.
    # This lets CRM create an email-only lead where supported.
    mobile_for_payload = mobile if mobile_valid else ""

    enquiry_source = clean_text(
        lead.get("In4 CRM CSV Final[Source Of Information]")
    )

    project_code = clean_text(
        lead.get("In4 CRM CSV Final[Project Code]")
    ).upper()

    # ============================================================
    # PROJECT MAPPING
    # ============================================================

    project_name = PROJECT_MAPPING.get(
        project_code,
        ""
    )

    if not project_name:
        print(f"Invalid Project Code: {project_code}")

        # Mark as failed/invalid in your existing processing logic
        # and continue to the next lead.
        return {
            "status": "invalid_project",
            "message": f"Invalid Project Code: {project_code}",
            "project_code": project_code
        }

    # --------------------------------------------------------
    # PROJECT MAPPING
    # --------------------------------------------------------

    crm_project_name = map_project(
        project_name
    )


    # --------------------------------------------------------
    # MOBILE / EMAIL VALIDATION
    # --------------------------------------------------------

    # Normal case: valid mobile -> push.
    #
    # Special case: invalid/blank mobile + valid email -> push.
    #
    # If both mobile and email are unusable, do not push.
    if not mobile_valid and not email_valid:

        return {
            "status": "invalid_mobile",
            "message": "Invalid Mobile and Email",
            "mobile": mobile,
            "email": email
        }


    # --------------------------------------------------------
    # SOURCE MAPPING
    # --------------------------------------------------------

    enquiry_source_name, enquiry_source_id = map_source(
        enquiry_source
    )


    # --------------------------------------------------------
    # COUNTRY CODE
    # --------------------------------------------------------

    country_code = clean_text(
        lead.get("In4 CRM CSV Final[Country Code]")
    ) or "+91"


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    title = clean_text(
        lead.get("In4 CRM CSV Final[Title]")
    ) or "Mr."


    # --------------------------------------------------------
    # PAYLOAD
    # --------------------------------------------------------

    payload = {

        "tokenId": token_id,

        "title": title,

        "leadFirstName": first_name,

        "leadLastName": last_name,

        "emailId": email,

        "countryCode": country_code,

        "mobileNo": mobile_for_payload,

        "dateOfBirth": "",

        "panNumber": "",

        "aadharNumber": "",

        "occupation": "",

        "enquirySource": enquiry_source_name,

        "enquirySourceId": enquiry_source_id,

        "enquirySourceReference": "",

        "subEnquirySource": "",

        "subEnquirySourceId": "",

        "leadAddress": "",

        "projectName": crm_project_name,

        "subProjectName": crm_project_name,

        "websiteURL": "https://pacerppacificacompanies.in",

        "vendorReferenceId": "",

        "additionalFieldList": []

    }


    # --------------------------------------------------------
    # API CALL
    # --------------------------------------------------------

    try:

        api_response = requests.post(
            CREATE_LEAD_URL,
            json=payload,
            timeout=30
        )



        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        try:

            response_json = api_response.json()

        except Exception:

            response_json = {
                "raw_response":
                api_response.text
            }


        if isinstance(
            response_json,
            list
        ):

            if response_json:

                response_data = response_json[0]

            else:

                response_data = {}

        else:

            response_data = response_json


        response_text = json.dumps(
            response_data
        ).lower().replace(
            " ",
            ""
        )



        # ----------------------------------------------------
        # DUPLICATE
        # ----------------------------------------------------

        if "leadalreadyexist" in response_text:


            return {
                "status": "duplicate",
                "message": "Duplicate",
                "response": response_data
            }


        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        elif (
            api_response.status_code == 200
            and "status" in response_text
        ):

            print(
                f"Uploaded - New Lead: {first_name} {last_name} | "
                f"{mobile} | {crm_project_name}"
            )

            return {
                "status": "uploaded",
                "message": "Uploaded",
                "response": response_data,
                "project": crm_project_name,
                "source": enquiry_source_name
            }


        # ----------------------------------------------------
        # FAILED
        # ----------------------------------------------------

        else:

            logger.error(
                "Failed Upload: %s",
                response_data
            )

            return {
                "status": "failed",
                "message": str(response_data),
                "response": response_data
            }


    except Exception as e:

        logger.error(
            "Critical API Error: %s",
            e
        )

        return {
            "status": "failed",
            "message": str(e)
        }


# ============================================================
# PROCESS MASTER CSV
# ============================================================

def process_master_csv(csv_file):

    print("=" * 70)
    print("IN4 MASTER CSV AUTOMATION")
    print("=" * 70)

    print(
        f"Processing File: {csv_file.name}"
    )

    print(
        f"Input Folder: {INPUT_FOLDER}"
    )

    print("=" * 70)


    # --------------------------------------------------------
    # READ CSV
    # --------------------------------------------------------

    try:

        df = pd.read_csv(
            csv_file,
            dtype=str
        ).fillna("")

    except Exception as e:

        logger.error(
            "Unable to read CSV: %s",
            e
        )

        return False


    # --------------------------------------------------------
    # CLEAN COLUMN NAMES
    # --------------------------------------------------------

    df.columns = [
        str(col).strip()
        for col in df.columns
    ]


    print(
        "CSV Columns:"
    )

    print(
        df.columns.tolist()
    )


    # --------------------------------------------------------
    # VALIDATE COLUMNS
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]


    if missing_columns:

        print("=" * 70)

        print(
            "ERROR - REQUIRED COLUMNS MISSING"
        )

        print(
            missing_columns
        )

        print("=" * 70)

        return False


    # --------------------------------------------------------
    # REMOVE COMPLETELY EMPTY ROWS
    # --------------------------------------------------------

    df = df.dropna(
        how="all"
    )


    total_count = len(df)


    print("=" * 70)

    print(
        f"TOTAL LEADS FOUND: {total_count}"
    )

    print("=" * 70)


    # ========================================================
    # GOOGLE SHEET DUPLICATE CHECKPOINT
    # ========================================================

    print()
    print("=" * 70)
    print("LOADING GOOGLE SHEET DUPLICATE CHECK")
    print("=" * 70)

    google_result = get_google_sheet_confirmed_mobiles()

    if not google_result.get("success"):

        print()
        print("GOOGLE SHEET CHECK FAILED")
        print(
            google_result.get(
                "message",
                "Unknown Google Sheet error"
            )
        )
        print()
        print("MASTER CSV UPLOAD STOPPED FOR SAFETY.")
        print("No CRM CreateSalesLead calls will be made.")
        print("=" * 70)

        return False

    google_confirmed_mobiles = google_result.get(
        "mobiles",
        set()
    )

    print(
        f"Confirmed Google Sheet Mobiles : {len(google_confirmed_mobiles)}"
    )
    print("=" * 70)


    # --------------------------------------------------------
    # COUNTERS
    # --------------------------------------------------------

    uploaded_count = 0

    duplicate_count = 0

    failed_count = 0

    invalid_mobile_count = 0

    token_failed_count = 0

    google_sheet_match_count = 0
    new_lead_candidate_count = 0


    # --------------------------------------------------------
    # SUMMARY STORAGE
    # --------------------------------------------------------

    uploaded_leads = []

    failed_leads = []

    project_stats = {}

    source_stats = {}


    # --------------------------------------------------------
    # PROCESS EACH LEAD
    # --------------------------------------------------------

    for index, row in df.iterrows():

        lead_number = index + 1


        # Convert row to dictionary
        lead = row.to_dict()


        first_name = clean_text(
            lead.get("First_Name")
        )

        last_name = clean_text(
            lead.get("Last_Name")
        )

        mobile = clean_mobile(
            lead.get("Preferred_Contact_No")
        )

        email = clean_text(
            lead.get("In4 CRM CSV Final[Email Id]")
        )

        email_valid = is_valid_email(email)
        mobile_valid = bool(mobile) and len(mobile) >= 10

        project_name = clean_text(
            lead.get("Project_Code")
        )

        crm_project = map_project(
            project_name
        )


        # ----------------------------------------------------
        # GOOGLE SHEET DUPLICATE CHECK
        # ----------------------------------------------------

        # Only a valid mobile can participate in the mobile-based
        # Google Sheet duplicate checkpoint.
        if mobile_valid and mobile in google_confirmed_mobiles:

            google_sheet_match_count += 1
            duplicate_count += 1

            # Do NOT call PUSH_TO_IN4_CRM().
            # This prevents CreateSalesLead from receiving an
            # already-uploaded lead and potentially reactivating it.
            continue

        # Valid mobile OR valid email is eligible for CRM push.
        if mobile_valid or email_valid:
            new_lead_candidate_count += 1
        else:
            new_lead_candidate_count += 1


        # ----------------------------------------------------
        # PUSH TO CRM
        # ----------------------------------------------------

        result = PUSH_TO_IN4_CRM(
            lead
        )


        status = result.get(
            "status"
        )


        # ----------------------------------------------------
        # UPLOADED
        # ----------------------------------------------------

        if status == "uploaded":

            uploaded_count += 1

            # Use the project returned by the IN4 CRM API function
            # because PUSH_TO_IN4_CRM() already reads the correct
            # Master CSV Project Code and applies the mapping.

            uploaded_project = result.get(
                "project",
                "Unknown"
            )

            project_stats[
                uploaded_project
            ] = project_stats.get(
                uploaded_project,
                0
            ) + 1


            source_name = result.get(
                "source",
                "Other"
            )


            source_stats[
                source_name
            ] = source_stats.get(
                source_name,
                0
            ) + 1


            uploaded_leads.append({

                "first_name": first_name,

                "last_name": last_name,

                "mobile": mobile,

                "email": clean_text(
                    lead.get("In4 CRM CSV Final[Email Id]")
                ),

                "project": crm_project,

                "source": source_name

            })


        # ----------------------------------------------------
        # DUPLICATE
        # ----------------------------------------------------

        elif status == "duplicate":

            duplicate_count += 1


        # ----------------------------------------------------
        # INVALID MOBILE
        # ----------------------------------------------------

        elif status == "invalid_mobile":

            invalid_mobile_count += 1

            failed_count += 1


            failed_leads.append({

                "first_name": first_name,

                "last_name": last_name,

                "mobile": mobile,

                "email": clean_text(
                    lead.get("In4 CRM CSV Final[Email Id]")
                ),

                "project": crm_project,

                "reason": "Invalid Mobile and Email"

            })


        # ----------------------------------------------------
        # TOKEN FAILED
        # ----------------------------------------------------

        elif status == "token_failed":

            token_failed_count += 1

            failed_count += 1


            failed_leads.append({

                "first_name": first_name,

                "last_name": last_name,

                "mobile": mobile,

                "email": clean_text(
                    lead.get("Email_ID")
                ),

                "project": crm_project,

                "reason": "Security Token Failed"

            })


        # ----------------------------------------------------
        # OTHER FAILURE
        # ----------------------------------------------------

        else:

            failed_count += 1


            failed_leads.append({

                "first_name": first_name,

                "last_name": last_name,

                "mobile": mobile,

                "email": clean_text(
                    lead.get("Email_ID")
                ),

                "project": crm_project,

                "reason": result.get(
                    "message",
                    "API Failed"
                )

            })


        # Small delay between leads
        time.sleep(0.2)


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print(f"NEW LEADS UPLOADED : {uploaded_count}")
    print("=" * 70)

    # ========================================================
    # SEND EMAIL
    # ========================================================

    send_report(

        csv_file=csv_file,

        total_count=total_count,

        uploaded_count=uploaded_count,

        duplicate_count=duplicate_count,

        failed_count=failed_count,

        invalid_mobile_count=invalid_mobile_count,

        token_failed_count=token_failed_count,

        project_stats=project_stats,

        source_stats=source_stats,

        failed_leads=failed_leads
    )


    # ========================================================
    # CREATE PROCESSED MARKER
    # ========================================================

    try:

        processed_file = Path(
            str(csv_file) + ".processed"
        )

        processed_file.write_text(
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            encoding="utf-8"
        )

        print()
        print(
            f"Processed marker created: "
            f"{processed_file.name}"
        )

    except Exception as e:

        logger.error(
            "Could not create processed marker: %s",
            e
        )


    print("=" * 70)

    print(
        "MASTER CSV AUTOMATION COMPLETED"
    )

    print("=" * 70)


    return True


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("YUKTI-AI - IN4 MASTER CSV PUSH")
    print("=" * 70)

    print(
        f"Watching folder:\n{INPUT_FOLDER}"
    )

    print("=" * 70)


    # --------------------------------------------------------
    # FIND CSV
    # --------------------------------------------------------

    csv_file = find_master_csv()


    if csv_file is None:

        print(
            "No Master CSV found."
        )

        return


    # --------------------------------------------------------
    # CHECK PROCESSED MARKER
    # --------------------------------------------------------

    processed_file = Path(
        str(csv_file) + ".processed"
    )


    if processed_file.exists():

        print()
        print(
            f"CSV already processed:"
        )

        print(
            csv_file.name
        )

        print()
        print(
            "No action required."
        )

        return


    # --------------------------------------------------------
    # PROCESS
    # --------------------------------------------------------

    process_master_csv(
        csv_file
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()