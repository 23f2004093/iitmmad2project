import os

from datetime import datetime, timedelta

from app import celery_app

from database import db

from models.user import StudentProfile

from models.job import Job

from models.application import Application



@celery_app.task(name="tasks.daily_reminders.send_daily_reminders")

def send_daily_reminders():

    today = datetime.utcnow().date()

    reminder_limit = today + timedelta(days=3)

    

    jobs = Job.query.filter_by(status="approved").all()

    upcoming_jobs = []

    

    for job in jobs:

        try:

            deadline_date = datetime.strptime(job.deadline, "%Y-%m-%d").date()

            if today <= deadline_date <= reminder_limit:

                upcoming_jobs.append(job)

        except Exception:

            continue



    if not upcoming_jobs:

        return 0



    students = StudentProfile.query.all()

    reminder_count = 0

    

    log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads", "notifications.log"))

    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    

    with open(log_path, mode="a", encoding="utf-8") as log_file:

        for job in upcoming_jobs:

            for s in students:

                already_applied = Application.query.filter_by(student_id=s.id, job_id=job.id).first()

                if not already_applied:

                    message = (

                        f"[{datetime.utcnow().isoformat()}] REMINDER: Dear {s.name}, "

                        f"the application deadline for '{job.title}' at "

                        f"'{job.company.company_name if job.company else 'Unknown'}' "

                        f"is approaching on {job.deadline}. Please apply."

                    )

                    log_file.write(message + "\n")

                    reminder_count += 1

                    

    return reminder_count

