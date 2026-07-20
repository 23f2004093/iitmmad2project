from flask import Flask, send_file, jsonify, send_from_directory
from config import Config
from database import db
from routes.auth import auth_bp
from routes.students import students_bp
from routes.jobs import jobs_bp
from routes.admin import admin_bp
import os

# Import models so Flask-SQLAlchemy metadata discovers them on db.create_all()
import models 

app = Flask(
    __name__,
    static_folder="../frontend",     # Serve static files from the /frontend directory
    static_url_path="/frontend"      # Requests starting with /frontend/ resolve here
)

# Load configurations
app.config.from_object(Config)

# Bind the database instance to Flask app context
db.init_app(app)

# Programmatically create all SQLite tables on app startup
with app.app_context():
    db.create_all()

# Register Blueprints
app.register_blueprint(admin_bp,url_prefix="/api/admin")
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(students_bp, url_prefix="/api/students")
app.register_blueprint(jobs_bp, url_prefix="/api/jobs")

# Route to serve student resume PDF uploads
@app.route("/uploads/<path:filename>")
def serve_uploads(filename):
    return send_from_directory(os.path.abspath(os.path.join(app.root_path, "uploads")), filename)

@app.route("/")
def index():
    # Serves the main index.html file directly from the frontend folder
    return send_file("../frontend/index.html")

@app.route("/api/test")
def test_api():
    return jsonify({
        "status": "success",
        "message": "Flask backend is running and database is connected!"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
