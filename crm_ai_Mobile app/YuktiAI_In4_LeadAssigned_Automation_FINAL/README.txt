YUKTI-AI IN4 LEAD ASSIGNED REPORT AUTOMATION

Validated against the supplied LeadAssignedReport (9).xlsx:
215 valid records, 7 projects, 3 sources.

Install:
    pip install pandas openpyxl

Configure DOWNLOAD_FOLDER and WORK_FOLDER in the Python file.

The current engine:
Downloads/reads LeadAssignedReport -> validates -> SQLite -> JSON summary -> Archive.

The next stage is browser automation of the In4 report page:
From Date -> To Date -> View Report -> Excel download.
That browser layer should call this tested parser afterward.

This is independent of OutlookExcelAutomation.py.
