from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models.user import User, StudentProfile, CompanyProfile

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register/student", methods=["POST"])
def register_student():
    data = request.get_json() or {}
    user_data = data.get("user_data", {})
    profile_data = data.get("profile_data", {})

    email = user_data.get("email")
    password = user_data.get("password")
    roll_number = profile_data.get("roll_number")

    if not email or not password or not roll_number:
        return jsonify({"status": "error", "message": "Email, password, and roll number are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"status": "error", "message": "Email is already registered"}), 400

    if StudentProfile.query.filter_by(roll_number=roll_number).first():
        return jsonify({"status": "error", "message": "Roll number is already registered"}), 400

    try:
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(
            email=email,
            password_hash=hashed_password,
            role="student"
        )
        db.session.add(new_user)
        db.session.flush()

        new_profile = StudentProfile(
            user_id=new_user.id,
            roll_number=roll_number,
            name=profile_data.get("name"),
            department=profile_data.get("department"),
            cgpa=float(profile_data.get("cgpa")) if profile_data.get("cgpa") else 0.0
        )

        db.session.add(new_profile)
        db.session.commit()

        return jsonify({"status": "success", "message": "Student registered successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Registration failed: {str(e)}"}), 500


@auth_bp.route("/register/recruiter", methods=["POST"])
def register_recruiter():
    data = request.get_json() or {}
    user_data = data.get("user_data", {})
    profile_data = data.get("profile_data", {})

    email = user_data.get("email")
    password = user_data.get("password")
    company_name = profile_data.get("company_name")

    if not email or not password or not company_name:
        return jsonify({"status": "error", "message": "Email, password, and company name are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"status": "error", "message": "Email is already registered"}), 400

    if CompanyProfile.query.filter_by(company_name=company_name).first():
        return jsonify({"status": "error", "message": "Company name is already registered"}), 400

    try:
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(
            email=email,
            password_hash=hashed_password,
            role="recruiter"
        )
        db.session.add(new_user)
        db.session.flush()

        new_profile = CompanyProfile(
            user_id=new_user.id,
            company_name=company_name,
            hr_contact=profile_data.get("hr_contact"),
            website=profile_data.get("website"),
            description=profile_data.get("description"),
            is_approved=False  # Requires admin approval
        )

        db.session.add(new_profile)
        db.session.commit()

        return jsonify({"status": "success", "message": "Company registered! Awaiting admin approval."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": " Company Registration Failed"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    # 1. Admin Login (Hardcoded credentials)
    if email == "admin@iitm.in" and password == "admin123":
        session["user_id"] = "admin"
        session["role"] = "admin"
        return jsonify({
            "status": "success",
            "message": "Welcome Administrator",
            "role": "admin"
        }), 200

    # 2. Database query for normal users
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    # Check if company is approved by admin
    if user.role == "recruiter" and not user.company_profile.is_approved:
        return jsonify({
            "status": "error",
            "message": "Your recruiter profile is pending approval from the placement cell admin."
        }), 403

    # Check if account is active
    if not user.is_active:
        return jsonify({"status": "error", "message": "Your account has been deactivated."}), 403

    # Store user identity in the signed session cookie
    session["user_id"] = user.id
    session["role"] = user.role

    return jsonify({
        "status": "success",
        "message": "Login successful",
        "role": user.role
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({
        "status": "success",
        "message": "Logged out successfully"
    }), 200


@auth_bp.route("/me", methods=["GET"])
def get_current_user_info():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    if user_id == "admin":
        return jsonify({
            "status": "success",
            "role": "admin",
            "user": {"email": "admin@iitm.in"}
        }), 200

    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    user_data = {
        "id": user.id,
        "email": user.email,
        "role": user.role
    }

    if user.role == "student" and user.student_profile:
        user_data["name"] = user.student_profile.name
        user_data["roll_number"] = user.student_profile.roll_number
    elif user.role == "recruiter" and user.company_profile:
        user_data["company_name"] = user.company_profile.company_name
        user_data["hr_contact"] = user.company_profile.hr_contact

    return jsonify({
        "status": "success",
        "role": user.role,
        "user": user_data
    }), 200

