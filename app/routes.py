from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from app.models import Student # Import Student model from models
import re

# Blueprint for routes
student_bp = Blueprint('student', __name__)

@student_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')

        # --- Acceptance Criterion 2: Validation (Required fields) ---
        if not student_id or not full_name or not email or not password:
            flash('All fields are required.', 'error')
            return redirect(url_for('student.register'))

        # --- Acceptance Criterion 2: Validation (Password strength) ---
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return redirect(url_for('student.register'))

        # --- Validation (Malformed email) ---
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email address format.', 'error')
            return redirect(url_for('student.register'))

        # --- Acceptance Criterion 3: Duplicate Check ---
        if Student.query.filter_by(student_id=student_id).first() or Student.query.filter_by(email=email).first():
            flash('Student ID or email already registered.', 'error')
            return redirect(url_for('student.register'))

        # --- Acceptance Criterion 1 & 4: Creation and Hashing ---
        new_student = Student(
            student_id=student_id,
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(password) # AC 4: Password hashing
        )

        try:
            db.session.add(new_student)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('student.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during registration: {str(e)}', 'error')
            return redirect(url_for('student.register'))

    return render_template('register.html')

@student_bp.route('/dashboard')
def dashboard():
    # Placeholder for a protected route
    return "Dashboard"