"""
YUKTI-AI BUSINESS AUTOMATION
IN4 CRM - Lead Assigned Report Automation

Reads the latest LeadAssignedReport Excel downloaded from In4 CRM,
validates it, creates a management summary, stores the data in SQLite,
and archives the source report.

This module is independent of the existing Outlook/CSV automation.
"""

from pathlib import Path
from datetime import datetime
import pandas as pd
import sqlite3, json, shutil, sys, traceback

DOWNLOAD_FOLDER = Path.home() / "Downloads"
WORK_FOLDER = Path(r"D:\Yukti-Ai Business Automation\In4 Lead Report Automation")
DB_FILE = WORK_FOLDER / "yuktiai_in4.db"
SUMMARY_FILE = WORK_FOLDER / "latest_summary.json"
ARCHIVE_FOLDER = WORK_FOLDER / "Archive"
REPORT_HINT = "LeadAssignedReport"

REQUIRED_COLUMNS = [
    "Customer Name", "Opportunity ID", "Contact Number", "Project Name",
    "Enquiry Source", "Assinged By", "Assinged To", "Assinged Date"
]

def find_latest_report():
    files = [p for p in DOWNLOAD_FOLDER.glob("*.xlsx")
             if REPORT_HINT.lower() in p.stem.lower()]
    if not files:
        raise FileNotFoundError(
            f"No '{REPORT_HINT}' Excel report found in {DOWNLOAD_FOLDER}"
        )
    return max(files, key=lambda p: p.stat().st_mtime)

def read_report(path):
    raw = pd.read_excel(path, header=None)
    header_row = None
    for i in range(min(20, len(raw))):
        values = {str(v).strip() for v in raw.iloc[i].tolist() if pd.notna(v)}
        if "Customer Name" in values and "Opportunity ID" in values:
            header_row = i
            break
    if header_row is None:
        raise ValueError("Could not find the Lead Assigned Report header.")

    df = raw.iloc[header_row + 1:].copy()
    df.columns = [str(v).strip() if pd.notna(v) else ""
                  for v in raw.iloc[header_row].tolist()]
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError("Report structure changed. Missing: " + ", ".join(missing))

    df = df[REQUIRED_COLUMNS].dropna(how="all").copy()

    for c in ["Customer Name","Contact Number","Project Name",
              "Enquiry Source","Assinged By","Assinged To"]:
        df[c] = df[c].fillna("").astype(str).str.strip()

    df["Opportunity ID"] = pd.to_numeric(df["Opportunity ID"], errors="coerce")
    df["Assinged Date"] = pd.to_datetime(df["Assinged Date"], errors="coerce")
    df = df[df["Opportunity ID"].notna()].copy()
    df["Opportunity ID"] = df["Opportunity ID"].astype("int64")

    if df.empty:
        raise ValueError("No valid lead records found.")
    return df

def counts(df, column):
    return {str(k): int(v) for k, v in df[column].value_counts().items()}

def create_summary(df, source_file):
    project_source = {}
    for project, group in df.groupby("Project Name"):
        project_source[str(project)] = counts(group, "Enquiry Source")

    return {
        "success": True,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_file": source_file.name,
        "record_count": int(len(df)),
        "report_date_from": (
            df["Assinged Date"].min().strftime("%Y-%m-%d")
            if df["Assinged Date"].notna().any() else None),
        "report_date_to": (
            df["Assinged Date"].max().strftime("%Y-%m-%d")
            if df["Assinged Date"].notna().any() else None),
        "project_wise": counts(df, "Project Name"),
        "source_wise": counts(df, "Enquiry Source"),
        "assigned_to_wise": counts(df, "Assinged To"),
        "assigned_by_wise": counts(df, "Assinged By"),
        "project_source_wise": project_source,
    }

def save_database(df):
    WORK_FOLDER.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    try:
        df.to_sql("lead_assignments", conn, if_exists="replace", index=False)
        for sql in [
            "CREATE INDEX IF NOT EXISTS idx_opp ON lead_assignments([Opportunity ID])",
            "CREATE INDEX IF NOT EXISTS idx_date ON lead_assignments([Assinged Date])",
            "CREATE INDEX IF NOT EXISTS idx_project ON lead_assignments([Project Name])",
            "CREATE INDEX IF NOT EXISTS idx_source ON lead_assignments([Enquiry Source])",
        ]:
            conn.execute(sql)
        conn.commit()
    finally:
        conn.close()

def main():
    print("=" * 60)
    print("YUKTI-AI - IN4 LEAD ASSIGNED REPORT AUTOMATION")
    print("=" * 60)

    report = find_latest_report()
    print("Report:", report)

    df = read_report(report)
    print("Valid leads:", len(df))

    save_database(df)

    WORK_FOLDER.mkdir(parents=True, exist_ok=True)
    summary = create_summary(df, report)
    SUMMARY_FILE.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    ARCHIVE_FOLDER.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(report, ARCHIVE_FOLDER / f"{report.stem}_{stamp}{report.suffix}")

    print("SUCCESS")
    print("Database:", DB_FILE)
    print("Summary:", SUMMARY_FILE)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("AUTOMATION ERROR:", e)
        traceback.print_exc()
        sys.exit(1)
