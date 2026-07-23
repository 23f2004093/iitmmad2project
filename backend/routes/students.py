import os
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
from database import db
from models.user import User, StudentProfile
from models.application import Application
from utils.cache import cache_clear_pattern

students_bp = Blueprint("students", __name__)

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, "exports"), exist_ok=True)

def get_current_user():
    user_id = session.get("user_id")
    if not user_id or user_id == "admin":
        return None
    return User.query.get(int(user_id))

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@students_bp.route("/me", methods=["GET"])
def get_student_profile():
    user = get_current_user()
    if not user or user.role != "student":
        return jsonify({"status": "error", "message": "Unauthorized student access"}), 401
    
    profile = user.student_profile
    if not profile:
        return jsonify({"status": "error", "message": "Student profile not found"}), 404
        
    return jsonify({
        "status": "success",
        "student": {
            "name": profile.name,
            "roll_number": profile.roll_number,
            "department": profile.department,
            "cgpa": profile.cgpa,
            "resume_path": profile.resume_path
        }
    }), 200

@students_bp.route("/profile", methods=["PUT"])
def update_student_profile():
    user = get_current_user()
    if not user or user.role != "student":
        return jsonify({"status": "error", "message": "Unauthorized student access"}), 401
    
    profile = user.student_profile
    if not profile:
        return jsonify({"status": "error", "message": "Student profile not found"}), 404
        
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    department = data.get("department", "").strip()
    cgpa = data.get("cgpa")
    
    if name:
        profile.name = name
    if department:
        profile.department = department
    if cgpa is not None:
        try:
            profile.cgpa = float(cgpa)
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid CGPA value"}), 400
            
    try:
        db.session.commit()
        cache_clear_pattern("admin_stats:*")
        return jsonify({"status": "success", "message": "Profile updated successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Failed to update profile: {str(e)}"}), 500

@students_bp.route("/resume", methods=["POST"])
def upload_resume():
    user = get_current_user()
    if not user or user.role != "student":
        return jsonify({"status": "error", "message": "Unauthorized student access"}), 401

    profile = user.student_profile
    if not profile:
        return jsonify({"status": "error", "message": "Student profile not found"}), 404

    if "resume" not in request.files:
        return jsonify({"status": "error", "message": "No file part in the request"}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "No file selected for upload"}), 400

    if file and allowed_file(file.filename):
        safe_name = secure_filename(f"resume_{profile.roll_number}.pdf")
        file_path = os.path.join(UPLOAD_FOLDER, safe_name)
        
        try:
            file.save(file_path)
            profile.resume_path = f"uploads/{safe_name}"
            db.session.commit()
            return jsonify({
                "status": "success",
                "message": "Resume uploaded successfully!",
                "resume_path": profile.resume_path
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": f"Failed to save resume: {str(e)}"}), 500
    
    return jsonify({"status": "error", "message": "Invalid file type. Only PDF files are allowed."}), 400

@students_bp.route("/applications", methods=["GET"])
def get_applications():
    user = get_current_user()
    if not user or user.role != "student":
        return jsonify({"status": "error", "message": "Unauthorized student access"}), 401

    profile = user.student_profile
    if not profile:
        return jsonify({"status": "error", "message": "Student profile not found"}), 404

    apps = Application.query.filter_by(student_id=profile.id).all()
    apps_data = [{
        "id": app.id,
        "job_id": app.job_id,
        "status": app.status,
        "applied_on": app.applied_on.isoformat() if app.applied_on else None,
        "job": {
            "title": app.job.title,
            "company_name": app.job.company.company_name if app.job.company else "Unknown Company",
            "job_type": app.job.job_type,
            "package_ctc": app.job.package_ctc
        }
    } for app in apps]

    return jsonify({
        "status": "success",
        "applications": apps_data
    }), 200

@students_bp.route("/export-applications", methods=["POST"])
def export_applications_csv():
    user = get_current_user()
    if not user or user.role != "student":
        return jsonify({"status": "error", "message": "Unauthorized student access"}), 401

    profile = user.student_profile
    if not profile:
        return jsonify({"status": "error", "message": "Student profile not found"}), 404

    from tasks.csv_export import export_student_applications_task
    try:
        task = export_student_applications_task.delay(profile.id)
        return jsonify({
            "status": "pending",
            "task_id": task.id
        }), 202
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to start export task: {str(e)}"}), 500

@students_bp.route("/export-status/<string:task_id>", methods=["GET"])
def export_status(task_id):
    from celery.result import AsyncResult
    from app import celery_app
    
    try:
        res = AsyncResult(task_id, app=celery_app)
        if res.state == "SUCCESS":
            return jsonify({
                "status": "success",
                "download_url": f"/uploads/exports/{res.result}"
            }), 200
        elif res.state == "FAILURE":
            return jsonify({
                "status": "failure",
                "message": str(res.info)
            }), 500
        else:
            return jsonify({
                "status": "pending"
            }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
