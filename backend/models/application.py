from database import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    status = db.Column(db.String(50), default="applied")  # 'applied', 'shortlisted', 'selected', 'rejected'
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)

    # Link back to student profile and target job drive
    student = db.relationship("StudentProfile", backref=db.backref("applications", lazy=True, cascade="all, delete-orphan"))
    job = db.relationship("Job", backref=db.backref("applications", lazy=True, cascade="all, delete-orphan"))
