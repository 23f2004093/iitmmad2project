from database import db
from datetime import datetime

class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company_profiles.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    job_type = db.Column(db.String(50), default="full-time")  # 'internship', 'full-time'
    package_ctc = db.Column(db.String(50), nullable=False)    # e.g., '12 LPA'
    deadline = db.Column(db.String(50), nullable=False)       # Deadline date
    min_cgpa = db.Column(db.Float, default=0.0)               # CGPA criteria filter
    status = db.Column(db.String(50), default="pending")      # 'pending' (requires admin approval), 'approved', 'closed'
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    # Link back to recruiter company profile details
    company = db.relationship("CompanyProfile", backref=db.backref("jobs", lazy=True))
