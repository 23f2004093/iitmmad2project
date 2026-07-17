import os
import csv
from flask import Blueprint, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
from database import db
from models.user import User, StudentProfile
from models.application import Application
from io import BytesIO

students_bp = Blueprint("students", __name__)

# Define the absolute directory path for uploads
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
ALLOWED_EXTENSIONS = {"pdf"}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_current_user():
    """
    Helper function to authenticate user via the Flask session cookie.
    """
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
        # Create a unique, safe filename using student roll number
        safe_name = secure_filename(f"resume_{profile.roll_number}.pdf")
        file_path = os.path.join(UPLOAD_FOLDER, safe_name)
        
        try:
            file.save(file_path)
            
            # Save the relative path that the web server will resolve
            # In database: uploads/resume_rollno.pdf
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

    # Fetch applications along with job details
    apps = Application.query.filter_by(student_id=profile.id).all()
    apps_data = []
    for app in apps:
        apps_data.append({
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
        })

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

    apps = Application.query.filter_by(student_id=profile.id).all()
    
    # Generate CSV in memory using StringIO
    si = StringIO() if False else None # we import io below
    import io
    si = io.StringIO()
    cw = csv.writer(si)
    
    # Write CSV header
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
    
    # Reset file pointer and convert to response bytes
    output_str = si.getvalue()
    si.close()
    
    mem_file = BytesIO(output_str.encode("utf-8"))
    
    return send_file(
        mem_file,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"applications_history_{profile.roll_number}.csv"
    )
