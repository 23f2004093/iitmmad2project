import os

from datetime import datetime, timedelta

from app import celery_app

from database import db

from models.user import StudentProfile, CompanyProfile

from models.job import Job

from models.application import Application



@celery_app.task(name="tasks.monthly_report.generate_monthly_report")

def generate_monthly_report():

    now = datetime.utcnow()

    first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    last_day_prev_month = first_day_this_month - timedelta(days=1)

    start_prev_month = last_day_prev_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    

    drives_conducted = Job.query.filter(Job.created_on >= start_prev_month, Job.created_on < first_day_this_month).count()

    applications_submitted = Application.query.filter(Application.applied_on >= start_prev_month, Application.applied_on < first_day_this_month).count()

    students_selected = Application.query.filter(Application.status == "selected", Application.applied_on >= start_prev_month, Application.applied_on < first_day_this_month).count()

    

    total_students = StudentProfile.query.count()

    total_companies = CompanyProfile.query.filter_by(is_approved=True).count()

    

    month_name = start_prev_month.strftime("%B %Y")

    file_month = start_prev_month.strftime("%Y_%m")

    

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Placement Activity Report - {month_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
        h1 {{ color: #0d6efd; border-bottom: 2px solid #0d6efd; padding-bottom: 10px; }}
        .card {{ background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 15px; margin: 15px 0; }}
        .title {{ font-size: 16px; font-weight: bold; color: #495057; }}
        .value {{ font-size: 28px; font-weight: bold; color: #212529; margin-top: 5px; }}
    </style>
</head>
<body>
    <h1>Placement Portal Activity Report - {month_name}</h1>
    <div class="card">
        <div class="title">Placement Drives Conducted</div>
        <div class="value">{drives_conducted}</div>
    </div>
    <div class="card">
        <div class="title">Applications Submitted</div>
        <div class="value">{applications_submitted}</div>
    </div>
    <div class="card">
        <div class="title">Students Selected</div>
        <div class="value">{students_selected}</div>
    </div>
    <h2>System Totals</h2>
    <p>Total Registered Students: {total_students}</p>
    <p>Approved Recruiter Partners: {total_companies}</p>
</body>
</html>
"""



    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads", "reports"))

    os.makedirs(reports_dir, exist_ok=True)

    report_filename = f"monthly_report_{file_month}.html"

    filepath = os.path.join(reports_dir, report_filename)

    

    with open(filepath, mode="w", encoding="utf-8") as f:

        f.write(html_content)

        

    log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads", "notifications.log"))

    with open(log_path, mode="a", encoding="utf-8") as log_file:

        log_file.write(f"[{now.isoformat()}] REPORT GENERATED: Monthly placement report for {month_name} generated at reports/{report_filename}\n")

        

    return report_filename

