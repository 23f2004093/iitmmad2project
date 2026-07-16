from flask import Flask, send_file, jsonify
from config import Config
from database import db
from routes.auth import auth_bp

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
app.register_blueprint(auth_bp, url_prefix="/api/auth")

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
