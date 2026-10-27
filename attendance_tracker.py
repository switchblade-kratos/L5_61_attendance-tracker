"""Student attendance tracker.

Marks daily attendance per student, computes attendance percentages,
applies the 75% exam-eligibility rule, exports a CSV report, and can
sync results to an ERP system or back up reports.
"""
import csv
import glob
import os
import ssl
import tarfile
from datetime import datetime

import requests

# Global attendance register
STUDENTS = {}
ERP_URL = "https://erp.college.example/api/attendance"
ERP_API_KEY = os.environ.get("ERP_API_KEY", "")
MIN_ATTENDANCE = 75


def add_student(roll_no, name, section="A"):
    """Register a student with an empty attendance record."""
    STUDENTS[roll_no] = {"name": name, "section": section, "records": []}


def mark_attendance(roll_no, date, status, register=None):
    """Record attendance for a student and update the date register."""
    if register is None:
        register = {}
    date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
    register.setdefault(date, []).append(roll_no)
    STUDENTS[roll_no]["records"].append((date, status))
    return register


def attendance_percentage(roll_no):
    """Return the whole-number attendance percentage (0 if no records)."""
    records = STUDENTS[roll_no]["records"]
    total = len(records)
    if total == 0:
        return 0
    present = len([r for r in records if r[1] == "P"])
    return int(present / total * 100)


def is_eligible(percentage):
    """Return True if the percentage meets the minimum requirement."""
    return percentage >= MIN_ATTENDANCE


def shortage_list():
    """Return roll numbers of students below the minimum attendance."""
    return [roll_no for roll_no in STUDENTS
            if not is_eligible(attendance_percentage(roll_no))]


def has_long_absence(roll_no, days=3):
    """Return True if the student was absent for `days` days in a row."""
    statuses = [status for (_, status) in STUDENTS[roll_no]["records"]]
    return any(statuses[i:i + days] == ["A"] * days
               for i in range(len(statuses) - days + 1))


def latest_date(roll_no):
    """Return the most recent attendance date for a student."""
    return max(record[0] for record in STUDENTS[roll_no]["records"])


def safe_cell(value):
    """Neutralise values that spreadsheets would treat as formulas."""
    text = str(value)
    if text.startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def export_csv(path="attendance.csv"):
    """Write the attendance percentages to a CSV file."""
    with open(path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["roll_no", "name", "percentage"])
        for roll_no, student in STUDENTS.items():
            writer.writerow([
                safe_cell(roll_no),
                safe_cell(student["name"]),
                attendance_percentage(roll_no),
            ])
    return path


def sync_to_erp(roll_no):
    """Send a student's attendance percentage to the ERP system."""
    payload = {"roll_no": roll_no, "pct": attendance_percentage(roll_no)}
    response = requests.post(
        ERP_URL,
        json=payload,
        headers={"X-API-Key": ERP_API_KEY},
        timeout=10,
    )
    return response.status_code


def backup_reports():
    """Archive all CSV reports into a compressed tar file."""
    with tarfile.open("reports_backup.tgz", "w:gz") as tar:
        for report in glob.glob("*.csv"):
            tar.add(report)


def legacy_channel():
    """Return a secure default TLS context."""
    return ssl.create_default_context()


def run_job(command, shell=False):
    """Describe a job to run (not executed here)."""
    return {"command": command, "shell": shell}


def schedule_reminders():
    """Describe the SMS reminder job for students with a shortage."""
    return run_job("send_sms --shortage", shell=False)


def main():
    """Run a short demo of the attendance tracker."""
    register = {}
    add_student("R01", "Aditi")
    add_student("R02", "=HYPERLINK(\"http://evil.example\",\"Bharat\")")
    for date, status in [("2026-09-01", "P"), ("2026-09-02", "P"),
                         ("2026-09-03", "L"), ("2026-09-04", "P"),
                         ("2026-09-05", "H")]:
        mark_attendance("R01", date, status, register)
    for date, status in [("2026-09-01", "P"), ("2026-09-01", "P"),
                         ("2026-09-02", "A"), ("2026-09-03", "A"),
                         ("2026-09-04", "A"), ("2026-9-3", "P")]:
        mark_attendance("R02", date, status, register)
    mark_attendance("R01", "2030-01-01", "P", register)
    print("R01 attendance %:", attendance_percentage("R01"))
    print("R02 attendance %:", attendance_percentage("R02"))
    print("Is 75% eligible?", is_eligible(75))
    print("Shortage list:", shortage_list())
    print("R02 long absence?", has_long_absence("R02"))
    print("R02 latest date:", latest_date("R02"))
    print("Register entries for 2026-09-01:", register["2026-09-01"])
    print("Exported to:", export_csv())
    print("Reminder job:", schedule_reminders())
    print("ERP sync skipped (no network)")


if __name__ == "__main__":
    main()
