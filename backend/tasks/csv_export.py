import os
import csv
from datetime import datetime
from app import celery_app
from database import db
from models.user import StudentProfile
from models.application import Application

@celery_app.task(name="tasks.csv_export.export_student_applications_task")
def export_student_applications_task(student_id):
    profile = StudentProfile.query.get(student_id)
    if not profile:
        raise ValueError(f"Student profile with ID {student_id} not found")
        
    apps = Application.query.filter_by(student_id=student_id).all()
    filename = f"export_{profile.roll_number}.csv"
    exports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads", "exports"))
    os.makedirs(exports_dir, exist_ok=True)
    filepath = os.path.join(exports_dir, filename)
    
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        cw = csv.writer(f)
        cw.writerow(["Student ID", "Roll Number", "Student Name", "Company Name", "Drive Title", "Application Status", "Applied On"])
        for app in apps:
            cw.writerow([
                profile.id,
                profile.roll_number,
                profile.name,
                app.job.company.company_name if app.job.company else "Unknown",
                app.job.title,
                app.status,
                app.applied_on.strftime("%Y-%m-%d %H:%M:%S") if app.applied_on else ""
            ])
            
    log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads", "notifications.log"))
    with open(log_path, mode="a", encoding="utf-8") as al:
        al.write(f"[{datetime.utcnow().isoformat()}] ALERT: CSV application history export completed for student {profile.name} ({profile.roll_number}). File saved: exports/{filename}\n")
        
    return filename
