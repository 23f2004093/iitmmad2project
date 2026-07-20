from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models.user import User, StudentProfile, CompanyProfile
from models.job import Job
from models.application import Application

admin_bp = Blueprint("admin", __name__)

def is_admin_logged_in():
    return session.get("role") == "admin"

@admin_bp.route("/stats", methods=["GET"])
def get_stats():
    if not is_admin_logged_in():
        return jsonify({"status": "error", "message": "admin access required"}), 403

    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.filter_by(is_approved=True).count()
    total_jobs = Job.query.filter_by(status="approved").count()
    placed_students = db.session.query(Application.student_id).filter_by(status="selected").distinct().count()

    placement_percentage = 0.0
    if total_students > 0:
        placement_percentage = (placed_students / total_students) * 100

    return jsonify({
        "status": "success",
        "stats": {
            "total_students": total_students,
            "total_companies": total_companies,
            "total_jobs": total_jobs,
            "placement_percentage": placement_percentage
        }
    }), 200

@admin_bp.route("/pending-recruiters", methods=["GET"])
def get_pending_recruiters():
    if not is_admin_logged_in():
        return jsonify({"status": "error", "message": "admin access required"}), 403

    pending = CompanyProfile.query.filter_by(is_approved=False).all()
    companies_data = []
    for comp in pending:
        companies_data.append({
            "id": comp.id,
            "company_name": comp.hr_contact,
            "website": comp.website,
            "description": comp.description
        })

    return jsonify({
        "status": "success",
        "pending_recruiters": companies_data
    }), 200

@admin_bp.route("/pending-drives", methods=["GET"])
def get_pending_drives():
    if not is_admin_logged_in():
        return jsonify({"status": "error", "message": "admin access required"}), 403

    pending = Job.query.filter_by(status="pending").all()
    drives_data = []
    for job in pending:
        drives_data.append({
            "id": job.id,
            "company_id": job.company_id,
            "title": job.title,
            "description": job.description,
            "package_ctc": job.package_ctc,
            "min_cgpa": job.min_cgpa
        })

    return jsonify({
        "status": "success",
        "pending_drives": drives_data
    }), 200

@admin_bp.route("/approve-recruiter/<int:profile_id>", methods=["POST"])
def approve_recruiter(profile_id):
    if not is_admin_logged_in():
        return jsonify({"status": "error", "message": "admin access required"}), 403

    profile = CompanyProfile.query.get(profile_id)
    if not profile:
        return jsonify({"status": "error", "message": "profile not found"}), 404

    try:
        profile.is_approved = True
        db.session.commit()
        return jsonify({"status": "success", "message": "successfully approved the profile"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "approval for the selected company/recruiter failed"}), 500

@admin_bp.route("/approve-drive/<int:job_id>", methods=["POST"])
def approve_drive(job_id):
    if not is_admin_logged_in():
        return jsonify({"status": "error", "message": "admin access required"}), 403

    job = Job.query.get(job_id)
    if not job:
        return jsonify({"status": "error", "message": "job not found"}), 404

    try:
        job.status = "approved"
        db.session.commit()
        return jsonify({"status": "success", "message": "drive approved successfully"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "approval for the selected drive failed"}), 500
