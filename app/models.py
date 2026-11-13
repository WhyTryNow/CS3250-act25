from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    courses = db.relationship('Course', backref='student', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    gpa = db.Column(db.Float, default=0.0)
    is_completed = db.Column(db.Boolean, default=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Course {self.title}>'

def calculate_gpa(course_grades):
    """Calculates the GPA for a course based on a list of grades (assuming simple 4.0 scale)."""
    if not course_grades:
        return 0.0
    
    total_points = 0
    for grade in course_grades:
        if isinstance(grade, (int, float)):
            # Assuming grade is a score out of 4.0
            total_points += grade
    
    if not course_grades:
        return 0.0
        
    return total_points / len(course_grades)

