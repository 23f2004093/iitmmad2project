import sys

import os

import time



                                      

backend_dir = r"c:\Users\bachc\Downloads\projectiitm\backend"

sys.path.insert(0, backend_dir)



from app import app, celery_app

from database import db

from models.user import User, StudentProfile, CompanyProfile

from models.job import Job

from models.application import Application

from tasks.csv_export import export_student_applications_task

from tasks.daily_reminders import send_daily_reminders

from tasks.monthly_report import generate_monthly_report



def setup_dummy_data():

    

       

    print("[Test Setup] Checking database records...")

    

                          

    company_user = User.query.filter_by(email="recruiter_test@iitm.in").first()

    if not company_user:

        company_user = User(email="recruiter_test@iitm.in", password_hash="dummy_hash", role="recruiter", is_active=True)

        db.session.add(company_user)

        db.session.commit()

        

    company_profile = CompanyProfile.query.filter_by(user_id=company_user.id).first()

    if not company_profile:

        company_profile = CompanyProfile(

            user_id=company_user.id,

            company_name="Test Tech Corp",

            hr_contact="1234567890",

            website="https://testtech.com",

            description="Diagnostic test recruiter.",

            is_approved=True

        )

        db.session.add(company_profile)

        db.session.commit()



                  

    job = Job.query.filter_by(company_id=company_profile.id).first()

    if not job:

        job = Job(

            company_id=company_profile.id,

            title="Software Test Engineer",

            description="Diagnostic test job description.",

            job_type="Full-Time",

            package_ctc="15 LPA",

            deadline="2026-12-31",

            min_cgpa=8.0,

            status="approved"

        )

        db.session.add(job)

        db.session.commit()



                

    student_user = User.query.filter_by(email="student_test@iitm.ac.in").first()

    if not student_user:

        student_user = User(email="student_test@iitm.ac.in", password_hash="dummy_hash", role="student", is_active=True)

        db.session.add(student_user)

        db.session.commit()

        

    student_profile = StudentProfile.query.filter_by(user_id=student_user.id).first()

    if not student_profile:

        student_profile = StudentProfile(

            user_id=student_user.id,

            roll_number="CS2026TEST",

            name="Diag Test Student",

            department="Computer Science",

            cgpa=9.0,

            resume_path="uploads/resume_test.pdf"

        )

        db.session.add(student_profile)

        db.session.commit()



                    

    app_record = Application.query.filter_by(student_id=student_profile.id, job_id=job.id).first()

    if not app_record:

        app_record = Application(

            student_id=student_profile.id,

            job_id=job.id,

            status="applied"

        )

        db.session.add(app_record)

        db.session.commit()



    print("[Test Setup] Database holds valid test records.")

    return student_profile.id



def test_async_tasks():

    with app.app_context():

                    

        student_id = setup_dummy_data()

        

        print("\n" + "="*50)

        print("STARTING CELERY ASYNC TASKS DIAGNOSTIC RUN")

        print("="*50)

        

                            

        print("\n[Test 1] Dispatching: export_student_applications_task...")

        task_csv = export_student_applications_task.delay(student_id)

        print(f"Task dispatched with ID: {task_csv.id}. Waiting for completion...")

        csv_filename = task_csv.get(timeout=15)

        print(f"[OK] Task CSV Export completed successfully! Filename returned: {csv_filename}")

        

                                    

        csv_path = os.path.join(backend_dir, "uploads", "exports", csv_filename)

        if os.path.exists(csv_path):

            print(f"[OK] Verified: CSV file exists physically at: {csv_path}")

        else:

            print(f"❌ Error: CSV file not found at: {csv_path}")



                                 

        print("\n[Test 2] Dispatching: send_daily_reminders...")

        task_reminders = send_daily_reminders.delay()

        print(f"Task dispatched with ID: {task_reminders.id}. Waiting for completion...")

        reminders_sent = task_reminders.get(timeout=15)

        print(f"[OK] Task Daily Reminders completed successfully! Reminders logged: {reminders_sent}")



                                

        print("\n[Test 3] Dispatching: generate_monthly_report...")

        task_report = generate_monthly_report.delay()

        print(f"Task dispatched with ID: {task_report.id}. Waiting for completion...")

        report_filename = task_report.get(timeout=15)

        print(f"[OK] Task Monthly Report completed successfully! HTML Report filename: {report_filename}")

        

                                   

        report_path = os.path.join(backend_dir, "uploads", "reports", report_filename)

        if os.path.exists(report_path):

            print(f"[OK] Verified: Monthly report HTML exists physically at: {report_path}")

        else:

            print(f"❌ Error: Report HTML file not found at: {report_path}")



                                 

        log_path = os.path.join(backend_dir, "uploads", "notifications.log")

        if os.path.exists(log_path):

            print(f"[OK] Verified: Notification logs written physically to: {log_path}")

                                        

            with open(log_path, 'r', encoding='utf-8') as lf:

                lines = lf.readlines()

                print("\nLast 3 lines of notifications.log:")

                for line in lines[-3:]:

                    print("  >", line.strip())

        else:

            print(f"❌ Error: notifications.log file not found at: {log_path}")



        print("\n" + "="*50)

        print("CELERY DIAGNOSTIC RUN COMPLETED SUCCESSFULLY!")

        print("="*50)



if __name__ == "__main__":

    test_async_tasks()

