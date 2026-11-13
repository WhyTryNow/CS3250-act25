from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import BootstrapMixin # Assuming we might need this for flash messages, though we will stick to basic Jinja2 flashes as per constraints.

db = SQLAlchemy()

def create_app(config_object=None):
    app = Flask(__name__)
    
    # Configuration (using a default SQLite setup for testing/development)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Secret key is necessary for sessions if we implemented auth, good practice to include.
    app.config['SECRET_KEY'] = 'a_very_secret_key_for_testing'

    db.init_app(app)

    # Blueprint registration
    from app.routes import main as main_bp
    app.register_blueprint(main_bp)

    # Context processor for flash messages (if needed, otherwise rely on standard Jinja context)
    # For simplicity and adherence to constraints, we rely on standard Flask flash messages
    
    with app.app_context():
        db.create_all()
        
    return app

