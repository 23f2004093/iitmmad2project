import uuid
from flask import Blueprint, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, redis_client
from models.user import User, StudentProfile, CompanyProfile

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register/student", methods=["POST"])
def register_student():
    """
    Registers a new student, hashes their password, and creates their profile.
    """
    data = request.get_json()
    user_data = data.get("user_data", {})
    profile_data = data.get("profile_data", {})

    # Check if email is already taken
    existing_user = User.query.filter_by(email=user_data.get("email")).first()
    if existing_user:
        return jsonify({"status": "error", "message": "Email is already registered"}), 400

    # Check if student roll number is already taken
    existing_roll = StudentProfile.query.filter_by(roll_number=profile_data.get("roll_number")).first()
    if existing_roll:
        return jsonify({"status": "error", "message": "Roll number is already registered"}), 400

    try:
        # 1. Create the User account record
        hashed_password = generate_password_hash(user_data.get("password"), method="pbkdf2:sha256")
        new_user = User(
            email=user_data.get("email"),
            password_hash=hashed_password,
            role="student"
        )
        db.session.add(new_user)
        db.session.commit()  # Generates new_user.id

        # 2. Create the associated Student Profile
        new_profile = StudentProfile(
            user_id=new_user.id,
            roll_number=profile_data.get("roll_number"),
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
    """
    Registers a new recruiter profile. Recruiter account is set to pending admin approval.
    """
    data = request.get_json()
    user_data = data.get("user_data", {})
    profile_data = data.get("profile_data", {})

    # Check if email is already taken
    existing_user = User.query.filter_by(email=user_data.get("email")).first()
    if existing_user:
        return jsonify({"status": "error", "message": "Email is already registered"}), 400

    try:
        # 1. Create the User account record
        hashed_password = generate_password_hash(user_data.get("password"), method="pbkdf2:sha256")
        new_user = User(
            email=user_data.get("email"),
            password_hash=hashed_password,
            role="recruiter"
        )
        db.session.add(new_user)
        db.session.commit()

        # 2. Create the associated Recruiter Profile (awaits admin approval)
        new_profile = CompanyProfile(
            user_id=new_user.id,
            company_name=profile_data.get("company_name"),
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
        return jsonify({"status": "error", "message": f"Registration failed: {str(e)}"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Verifies user credentials, sets up a secure session ID inside Redis,
    and returns the role mapping to the Vue client.
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # 1. Hardcoded Check for Admin
    if email == "admin@iitm.in" and password == "admin123":
        session_token = str(uuid.uuid4())
        # Store admin session in Redis for 24 hours
        redis_client.setex(session_token, 3600 * 24, "admin")
        
        response = make_response(jsonify({
            "status": "success",
            "message": "Welcome Administrator",
            "role": "admin"
        }), 200)
        
        response.set_cookie(
            "session_id",
            session_token,
            httponly=True,
            max_age=3600 * 24,
            samesite="Lax"
        )
        return response

    # 2. Database query check for Students and Recruiters
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    # Check if recruiter is approved by the admin
    if user.role == "recruiter" and not user.company_profile.is_approved:
        return jsonify({
            "status": "error",
            "message": "Your recruiter profile is pending approval from the placement cell admin."
        }), 403

    # Check if user account is deactivated
    if not user.is_active:
        return jsonify({"status": "error", "message": "Your account has been deactivated."}), 403

    # Generate unique session ID token
    session_token = str(uuid.uuid4())
    # Save the session mapping: session_token -> user_id in Redis (expires in 24 hours)
    redis_client.setex(session_token, 3600 * 24, str(user.id))

    response = make_response(jsonify({
        "status": "success",
        "message": "Login successful",
        "role": user.role
    }), 200)

    # Set secure session cookie
    response.set_cookie(
        "session_id",
        session_token,
        httponly=True,
        max_age=3600 * 24,
        samesite="Lax"
    )
    return response


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Terminates the session inside Redis and clears the client session cookie.
    """
    session_id = request.cookies.get("session_id")
    if session_id:
        redis_client.delete(session_id)
        
    response = make_response(jsonify({
        "status": "success",
        "message": "Logged out successfully"
    }), 200)
    
    response.delete_cookie("session_id")
    return response