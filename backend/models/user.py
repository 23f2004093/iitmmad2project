from database import db



class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(128), nullable=False)

    role = db.Column(db.String(20), nullable=False)                                   

    is_active = db.Column(db.Boolean, default=True)                                      



                   

    student_profile = db.relationship("StudentProfile", backref="user", uselist=False, cascade="all, delete-orphan")

    company_profile = db.relationship("CompanyProfile", backref="user", uselist=False, cascade="all, delete-orphan")





class StudentProfile(db.Model):

    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    roll_number = db.Column(db.String(50), unique=True, nullable=False, index=True)

    name = db.Column(db.String(100), nullable=False)

    department = db.Column(db.String(100), nullable=False)

    cgpa = db.Column(db.Float, nullable=True)

    resume_path = db.Column(db.String(255), nullable=True)                                          





class CompanyProfile(db.Model):

    __tablename__ = "company_profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    company_name = db.Column(db.String(100), unique=True, nullable=False, index=True)

    hr_contact = db.Column(db.String(50), nullable=False)

    website = db.Column(db.String(255), nullable=False)

    description = db.Column(db.Text, nullable=True)

    is_approved = db.Column(db.Boolean, default=False)                                                 

