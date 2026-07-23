from flask import Blueprint, request, jsonify, session
from database import db
from models.user import User
from models.job import Job
from models.application import Application
from datetime import datetime
from utils.cache import cached_api

jobs_bp = Blueprint("jobs", __name__)

def get_current_user():
    user_id = session.get("user_id")
    if not user_id or user_id == "admin":
        return None
    return User.query.get(int(user_id))

@jobs_bp.route("/", methods=["GET"])
@cached_api(key_prefix="jobs_approved", timeout=120)
def get_approved_jobs():
    user = get_current_user()
    if not user:
        return jsonify({"status": "error", "message": "Unauthorized access"}), 401

    approved_jobs = Job.query.filter_by(status="approved").all()
    jobs_data = []
    for job in approved_jobs:
        jobs_data.append({
            "id": job.id,
            "company_id": job.company_id,
            "company_name": job.company.company_name if job.company else "Unknown Company",
            "title": job.title,
            "description": job.description,
            "job_type": job.job_type,
            "package_ctc": job.package_ctc,
            "deadline": job.deadline,
            "min_cgpa": job.min_cgpa,
            "status": job.status
        })

    return jsonify({
        "status": "success",
        "jobs": jobs_data
    }), 200

@jobs_bp.route("/<int:job_id>/apply", methods=["POST"])
def apply_to_job(job_id):
    user = get_current_user()
    if not user or user.role != "student":
        return jsonify({"status": "error", "message": "Only students can apply to placement drives"}), 401

    profile = user.student_profile
    if not profile:
        return jsonify({"status": "error", "message": "Student profile not found"}), 404

    job = Job.query.get(job_id)
    if not job or job.status != "approved":
        return jsonify({"status": "error", "message": "Placement drive is either invalid or not approved"}), 404

    existing_app = Application.query.filter_by(student_id=profile.id, job_id=job_id).first()
    if existing_app:
        return jsonify({"status": "error", "message": "You have already applied to this placement drive"}), 400

    if profile.cgpa is None or float(profile.cgpa) < float(job.min_cgpa):
        return jsonify({
            "status": "error", 
            "message": f"Your CGPA ({profile.cgpa}) does not meet the minimum eligibility criteria ({job.min_cgpa}) for this job."
        }), 400

    if not profile.resume_path:
        return jsonify({"status": "error", "message": "Please upload your resume before applying."}), 400

    try:
        new_application = Application(
            student_id=profile.id,
            job_id=job_id,
            status="applied",
            applied_on=datetime.utcnow()
        )
        db.session.add(new_application)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Application submitted successfully!"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Failed to submit application: {str(e)}"}), 500