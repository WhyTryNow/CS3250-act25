from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Blueprint for routes
student_bp = Blueprint('student', __name__)

# SQLAlchemy instance (will be initialized in create_app)
db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Student {self.student_id}>'

@student_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')

        # --- Acceptance Criterion 2: Validation ---
        if not student_id or not full_name or not email or not password:
            flash('All fields are required.', 'error')
            return redirect(url_for('student.register'))

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return redirect(url_for('student.register'))

        # Check for duplicate student ID or email
        if Student.query.filter_by(student_id=student_id).first() or Student.query.filter_by(email=email).first():
            flash('Student ID or email already registered.', 'error')
            return redirect(url_for('student.register'))

        # --- Acceptance Criterion 1 & 4: Creation and Hashing ---
        new_student = Student(
            student_id=student_id,
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(password)
        )

        try:
            db.session.add(new_student)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('student.dashboard')) # Assuming a dashboard exists
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during registration: {str(e)}', 'error')
            return redirect(url_for('student.register'))

    return render_template('register.html')

@student_bp.route('/dashboard')
def dashboard():
    # Placeholder for a protected route
    return "Dashboard"

# Placeholder for app/__init__.py content - must be created/verified
def create_app(config=None):
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from werkzeug.security import generate_password_hash, check_password_hash
    
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'a_very_secret_key_for_session' # Needed for sessions/flashing
    db = SQLAlchemy(app)

    # Register Blueprint
    app.register_blueprint(student_bp)

    with app.app_context():
        db.create_all()

    return app