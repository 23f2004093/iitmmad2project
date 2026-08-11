from flask import Blueprint, request, jsonify, session

from database import db

from models.user import CompanyProfile, StudentProfile

from models.job import Job

from models.application import Application

from utils.cache import cache_clear_pattern



companies_bp = Blueprint("companies", __name__)



@companies_bp.before_request

def restrict_to_recruiter():

    if session.get("role") != "recruiter":

        return jsonify({"status": "error", "message": "Recruiter authorization required"}), 403



def get_current_company():

    user_id = session.get("user_id")

    return CompanyProfile.query.filter_by(user_id=user_id).first()



@companies_bp.route("/dashboard", methods=["GET"])

def get_dashboard():

    company = get_current_company()

    if not company:

        return jsonify({"status": "error", "message": "Company profile not found"}), 404



    jobs = Job.query.filter_by(company_id=company.id).all()

    drives_data = []

    for job in jobs:

        applicant_count = Application.query.filter_by(job_id=job.id).count()

        drives_data.append({

            "id": job.id,

            "title": job.title,

            "description": job.description,

            "job_type": job.job_type,

            "package_ctc": job.package_ctc,

            "deadline": job.deadline,

            "min_cgpa": job.min_cgpa,

            "status": job.status,

            "created_on": job.created_on.strftime("%Y-%m-%d") if job.created_on else "",

            "applicant_count": applicant_count

        })



    return jsonify({

        "status": "success",

        "company": {

            "id": company.id,

            "company_name": company.company_name,

            "hr_contact": company.hr_contact,

            "website": company.website,

            "description": company.description,

            "is_approved": company.is_approved

        },

        "drives": drives_data

    }), 200



@companies_bp.route("/jobs", methods=["POST"])

def create_job_drive():

    company = get_current_company()

    if not company:

        return jsonify({"status": "error", "message": "Company profile not found"}), 404



    if not company.is_approved:

        return jsonify({"status": "error", "message": "Your company profile is pending Admin approval. You cannot post drives yet."}), 403



    data = request.get_json() or {}

    title = data.get("title", "").strip()

    description = data.get("description", "").strip()

    job_type = data.get("job_type", "Full-Time").strip()

    package_ctc = data.get("package_ctc", "").strip()

    deadline = data.get("deadline", "").strip()

    min_cgpa = data.get("min_cgpa", 0.0)



    if not title or not package_ctc or not deadline:

        return jsonify({"status": "error", "message": "Job title, package CTC, and application deadline are required"}), 400



    try:

        new_job = Job(

            company_id=company.id,

            title=title,

            description=description,

            job_type=job_type,

            package_ctc=package_ctc,

            deadline=deadline,

            min_cgpa=float(min_cgpa),

            status="pending"

        )

        db.session.add(new_job)

        db.session.commit()

        cache_clear_pattern("admin_stats:*")

        return jsonify({"status": "success", "message": "Placement drive submitted for Admin approval!"}), 201

    except Exception as e:

        db.session.rollback()

        return jsonify({"status": "error", "message": f"Failed to create drive: {str(e)}"}), 500



@companies_bp.route("/drives/<int:job_id>/applications", methods=["GET"])

def get_drive_applications(job_id):

    company = get_current_company()

    job = Job.query.get(job_id)

    if not job or job.company_id != company.id:

        return jsonify({"status": "error", "message": "Drive not found or access denied"}), 404



    apps = Application.query.filter_by(job_id=job.id).all()

    applicants_data = [{

        "application_id": app.id,

        "student_id": app.student.id if app.student else None,

        "student_name": app.student.name if app.student else "Unknown",

        "roll_number": app.student.roll_number if app.student else "N/A",

        "department": app.student.department if app.student else "N/A",

        "cgpa": app.student.cgpa if app.student else 0.0,

        "resume_path": app.student.resume_path if app.student else "",

        "status": app.status,

        "applied_on": app.applied_on.strftime("%Y-%m-%d %H:%M") if app.applied_on else ""

    } for app in apps]



    return jsonify({

        "status": "success",

        "job_title": job.title,

        "applicants": applicants_data

    }), 200



@companies_bp.route("/applications/<int:app_id>/status", methods=["POST"])

def update_application_status(app_id):

    company = get_current_company()

    app_record = Application.query.get(app_id)

    if not app_record or app_record.job.company_id != company.id:

        return jsonify({"status": "error", "message": "Application record not found or access denied"}), 404



    data = request.get_json() or {}

    new_status = data.get("status", "").strip().lower()

    if new_status not in ["applied", "shortlisted", "selected", "rejected"]:

        return jsonify({"status": "error", "message": "Invalid status value"}), 400



    try:

        app_record.status = new_status

        db.session.commit()

        cache_clear_pattern("admin_stats:*")

        return jsonify({"status": "success", "message": f"Student status updated to {new_status.upper()}"}), 200

    except Exception as e:

        db.session.rollback()

        return jsonify({"status": "error", "message": f"Failed to update status: {str(e)}"}), 500



@companies_bp.route("/jobs/<int:job_id>", methods=["PUT"])

def edit_job_drive(job_id):

    company = get_current_company()

    job = Job.query.get(job_id)

    if not job or job.company_id != company.id:

        return jsonify({"status": "error", "message": "Drive not found or access denied"}), 404

        

    data = request.get_json() or {}

    title = data.get("title", "").strip()

    description = data.get("description", "").strip()

    job_type = data.get("job_type", "").strip()

    package_ctc = data.get("package_ctc", "").strip()

    deadline = data.get("deadline", "").strip()

    min_cgpa = data.get("min_cgpa")



    if title:

        job.title = title

    if description:

        job.description = description

    if job_type:

        job.job_type = job_type

    if package_ctc:

        job.package_ctc = package_ctc

    if deadline:

        job.deadline = deadline

    if min_cgpa is not None:

        try:

            job.min_cgpa = float(min_cgpa)

        except ValueError:

            return jsonify({"status": "error", "message": "Invalid CGPA"}), 400



    try:

        db.session.commit()

        cache_clear_pattern("admin_stats:*")

        cache_clear_pattern("jobs_approved:*")

        return jsonify({"status": "success", "message": "Placement drive updated successfully!"}), 200

    except Exception as e:

        db.session.rollback()

        return jsonify({"status": "error", "message": f"Failed to update drive: {str(e)}"}), 500



@companies_bp.route("/jobs/<int:job_id>", methods=["DELETE"])

def delete_job_drive(job_id):

    company = get_current_company()

    job = Job.query.get(job_id)

    if not job or job.company_id != company.id:

        return jsonify({"status": "error", "message": "Drive not found or access denied"}), 404

        

    try:

        db.session.delete(job)

        db.session.commit()

        cache_clear_pattern("admin_stats:*")

        cache_clear_pattern("jobs_approved:*")

        return jsonify({"status": "success", "message": "Placement drive deleted successfully!"}), 200

    except Exception as e:

        db.session.rollback()

        return jsonify({"status": "error", "message": f"Failed to delete drive: {str(e)}"}), 500



@companies_bp.route("/jobs/<int:job_id>/close", methods=["POST"])

def close_job_drive(job_id):

    company = get_current_company()

    job = Job.query.get(job_id)

    if not job or job.company_id != company.id:

        return jsonify({"status": "error", "message": "Drive not found or access denied"}), 404

        

    try:

        job.status = "closed"

        db.session.commit()

        cache_clear_pattern("admin_stats:*")

        cache_clear_pattern("jobs_approved:*")

        return jsonify({"status": "success", "message": "Placement drive closed successfully!"}), 200

    except Exception as e:

        db.session.rollback()

        return jsonify({"status": "error", "message": f"Failed to close drive: {str(e)}"}), 500
