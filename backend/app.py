from flask import Flask, send_file, jsonify, send_from_directory

from config import Config

from database import db

from routes.auth import auth_bp

from routes.students import students_bp

from routes.jobs import jobs_bp

from routes.admin import admin_bp

from routes.companies import companies_bp

import os

import models 

from celery import Celery

from celery.schedules import crontab



app = Flask(

    __name__,

    static_folder="../frontend",

    static_url_path="/frontend"

)



app.config.from_object(Config)

db.init_app(app)



celery_app = Celery("app")

celery_app.conf.update(

    broker_url=app.config["CELERY_BROKER_URL"],

    result_backend=app.config["CELERY_RESULT_BACKEND"],

    timezone="Asia/Kolkata",

    enable_utc=True,

    imports=(

        "tasks.csv_export",

        "tasks.daily_reminders",

        "tasks.monthly_report"

    ),

    beat_schedule={

        "send-daily-reminders": {

            "task": "tasks.daily_reminders.send_daily_reminders",

            "schedule": crontab(hour=0, minute=0)

        },

        "generate-monthly-report": {

            "task": "tasks.monthly_report.generate_monthly_report",

            "schedule": crontab(day_of_month=1, hour=0, minute=0)

        }

    }

)



class ContextTask(celery_app.Task):

    def __call__(self, *args, **kwargs):

        with app.app_context():

            return self.run(*args, **kwargs)



celery_app.Task = ContextTask



with app.app_context():

    db.create_all()

    from werkzeug.security import generate_password_hash

    from models.user import User

    if not User.query.filter_by(role="admin").first():

        admin_user = User(

            email="admin@iitm.in",

            password_hash=generate_password_hash("admin123", method="pbkdf2:sha256"),

            role="admin",

            is_active=True

        )

        db.session.add(admin_user)

        db.session.commit()



app.register_blueprint(admin_bp, url_prefix="/api/admin")

app.register_blueprint(companies_bp, url_prefix="/api/companies")

app.register_blueprint(auth_bp, url_prefix="/api/auth")

app.register_blueprint(students_bp, url_prefix="/api/students")

app.register_blueprint(jobs_bp, url_prefix="/api/jobs")



@app.route("/uploads/<path:filename>")

def serve_uploads(filename):

    return send_from_directory(os.path.abspath(os.path.join(app.root_path, "uploads")), filename)



@app.route("/")

def index():

    return send_file("../frontend/index.html")



@app.route("/api/test")

def test_api():

    return jsonify({

        "status": "success",

        "message": "Flask backend is running and database is connected!"

    })



if __name__ == "__main__":

    app.run(debug=True, port=5000)

