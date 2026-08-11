from flask import Blueprint, request, jsonify, session

from database import db

from models.user import User, StudentProfile, CompanyProfile

from models.job import Job

from models.application import Application

from sqlalchemy import or_

from utils.cache import cached_api, cache_clear_pattern



admin_bp = Blueprint("admin", __name__)



@admin_bp.before_request

def restrict_to_admin():

    if session.get("role") != "admin":

        return jsonify({"status": "error", "message": "Admin access required"}), 403



@admin_bp.route("/stats", methods=["GET"])

@cached_api(key_prefix="admin_stats", timeout=300)

def get_stats():

    total_students = StudentProfile.query.count()

    total_companies = CompanyProfile.query.filter_by(is_approved=True).count()

    total_jobs = Job.query.filter_by(status="approved").count()

    placed_students = db.session.query(Application.student_id).filter_by(status="selected").distinct().count()



    placement_percentage = (placed_students / total_students) * 100 if total_students > 0 else 0.0



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

    pending = CompanyProfile.query.filter_by(is_approved=False).all()

    companies_data = [{

        "id": comp.id,

        "company_name": comp.company_name,

        "hr_contact": comp.hr_contact,

        "website": comp.website,

        "description": comp.description

    } for comp in pending]



    return jsonify({"status": "success", "pending_recruiters": companies_data}), 200



@admin_bp.route("/pending-drives", methods=["GET"])

def get_pending_drives():

    pending = Job.query.filter_by(status="pending").all()

    drives_data = [{

        "id": job.id,

        "company_id": job.company_id,

        "company_name": job.company.company_name if job.company else "Unknown Company",

        "title": job.title,

        "description": job.description,

        "package_ctc": job.package_ctc,

        "min_cgpa": job.min_cgpa

    } for job in pending]



    return jsonify({"status": "success", "pending_drives": drives_data}), 200



@admin_bp.route("/approve-recruiter/<int:profile_id>", methods=["POST"])

def approve_recruiter(profile_id):

    profile = CompanyProfile.query.get(profile_id)

    if not profile:

        return jsonify({"status": "error", "message": "Company profile not found"}), 404



    try:

        profile.is_approved = True

        db.session.commit()

        cache_clear_pattern("admin_stats:*")

        return jsonify({"status": "success", "message": "Recruiter approved successfully"}), 200

    except Exception as e:

        db.session.rollback()

        return jsonify({"status": "error", "message": f"Approval failed: {str(e)}"}), 500



@admin_bp.route("/reject-recruiter/<int:profile_id>", methods=["POST"])

def reject_recruiter(profile_id):

    profile = CompanyProfile.query.get(profile_id)

    if not profile:

        return jsonify({"status": "error", "message": "Company profile not found"}), 404



    try:

        user = User.query.get(profile.user_id)

        db.session.delete(profile)

        if user:

            db.session.delete(user)

        db.session.commit()

        cache_clear_pattern("admin_stats:*")

        return jsonify({"status": "success", "message": "Company registration rejected and removed"}), 200

    except Exception as e:

        db.session.rollback()

        return jsonify({"status": "error", "message": f"Rejection failed: {str(e)}"}), 500



@admin_bp.route("/approve-drive/<int:job_id>", methods=["POST"])

def approve_drive(job_id):

    job = Job.query.get(job_id)

    if not job:

        return jsonify({"status": "error", "message": "Placement drive not found"}), 404



    try:

        job.status = "approved"

        db.session.commit()

        cache_clear_pattern("admin_stats:*")

        cache_clear_pattern("jobs_approved:*")

        return jsonify({"status": "success", "message": "Placement drive approved"}), 200

    except Exception as e:

        db.session.rollback()

        return jsonify({"status": "error", "message": f"Approval failed: {str(e)}"}), 500



@admin_bp.route("/reject-drive/<int:job_id>", methods=["POST"])

def reject_drive(job_id):

    job = Job.query.get(job_id)

    if not job:

        return jsonify({"status": "error", "message": "Placement drive not found"}), 404



    try:

        job.status = "rejected"

        db.session.commit()

        cache_clear_pattern("admin_stats:*")

        return jsonify({"status": "success", "message": "Placement drive rejected"}), 200

    except Exception as e:

        db.session.rollback()

        return jsonify({"status": "error", "message": f"Rejection failed: {str(e)}"}), 500



@admin_bp.route("/students", methods=["GET"])

def get_all_students():

    students = StudentProfile.query.all()

    students_data = [{

        "user_id": s.user_id,

        "name": s.name,

        "roll_number": s.roll_number,

        "department": s.department,

        "cgpa": s.cgpa,

        "resume_path": s.resume_path,

        "is_active": s.user.is_active if s.user else True

    } for s in students]



    return jsonify({"status": "success", "students": students_data}), 200



@admin_bp.route("/applications", methods=["GET"])

def get_all_applications():

    apps = Application.query.all()

    apps_data = [{

        "id": app.id,

        "student_name": app.student.name if app.student else "Unknown",

        "student_roll": app.student.roll_number if app.student else "Unknown",

        "company_name": app.job.company.company_name if (app.job and app.job.company) else "Unknown",

        "job_title": app.job.title if app.job else "Unknown",

        "status": app.status,

        "applied_on": app.applied_on.strftime("%Y-%m-%d %H:%M") if app.applied_on else ""

    } for app in apps]



    return jsonify({"status": "success", "applications": apps_data}), 200



@admin_bp.route("/search", methods=["GET"])

def search_portal():

    query = request.args.get("query", "").strip()

    if not query:

        return jsonify({"status": "error", "message": "Query parameter is required"}), 400



    matching_students = StudentProfile.query.filter(

        or_(

            StudentProfile.name.ilike(f"%{query}%"),

            StudentProfile.roll_number.ilike(f"%{query}%"),

            StudentProfile.department.ilike(f"%{query}%")

        )

    ).all()



    matching_companies = CompanyProfile.query.filter(

        CompanyProfile.company_name.ilike(f"%{query}%")

    ).all()



    students_data = [{

        "user_id": s.user_id,

        "name": s.name,

        "roll_number": s.roll_number,

        "department": s.department,

        "cgpa": s.cgpa,

        "is_active": s.user.is_active if s.user else True

    } for s in matching_students]



    companies_data = [{

        "user_id": c.user_id,

        "company_name": c.company_name,

        "hr_contact": c.hr_contact,

        "website": c.website,

        "is_approved": c.is_approved,

        "is_active": c.user.is_active if c.user else True

    } for c in matching_companies]



    return jsonify({

        "status": "success",

        "students": students_data,

        "companies": companies_data

    }), 200



@admin_bp.route("/toggle-user-status/<int:user_id>", methods=["POST"])

def toggle_user_status(user_id):

    user = User.query.get(user_id)

    if not user:

        return jsonify({"status": "error", "message": "User not found"}), 404



    try:

        user.is_active = not user.is_active

        db.session.commit()

        cache_clear_pattern("admin_stats:*")

        return jsonify({"status": "success", "message": "User status updated"}), 200

    except Exception as e:

        db.session.rollback()

        return jsonify({"status": "error", "message": f"Failed to update user status: {str(e)}"}), 500



@admin_bp.route("/drives", methods=["GET"])

def get_all_drives():

    drives = Job.query.all()

    drives_data = [{

        "id": d.id,

        "title": d.title,

        "company_name": d.company.company_name if d.company else "Unknown Company",

        "package_ctc": d.package_ctc,

        "deadline": d.deadline,

        "min_cgpa": d.min_cgpa,

        "status": d.status,

        "applicant_count": Application.query.filter_by(job_id=d.id).count()

    } for d in drives]

    return jsonify({"status": "success", "drives": drives_data}), 200



@admin_bp.route("/drives/<int:job_id>/applications", methods=["GET"])

def get_drive_applicants(job_id):

    job = Job.query.get_or_404(job_id)

    apps = Application.query.filter_by(job_id=job_id).all()

    applicants_data = [{

        "application_id": app.id,

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

        "company_name": job.company.company_name if job.company else "Unknown",

        "applicants": applicants_data

    }), 200

