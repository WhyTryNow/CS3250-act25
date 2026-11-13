from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def create_app(config=None):
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'a_very_secret_key_for_session' # Required for sessions/flashing

    db.init_app(app)

    # Import and register blueprint
    from app.routes import student_bp
    app.register_blueprint(student_bp)

    with app.app_context():
        # This will create tables if they don't exist
        db.create_all()

    return app