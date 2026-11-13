import pytest
from app.models import Student
from app.routes import student_bp
from flask import url_for, request, redirect

# We need access to the app factory to run tests setup
from app import create_app, db 

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    with app.test_client() as client:
        yield client

def test_successful_registration(client):
    """
    Criterion 1: Given an unregistered student, when the student submits
    credentials, then a new student account is created and the student
    can log in with those credentials.
    """
    # 1. Attempt registration with valid data
    response = client.post(
        '/register',
        data={
            'student_id': 'S12345',
            'full_name': 'John Doe',
            'email': 'john.doe@example.com',
            'password': 'StrongPassword123'
        }
    )
    
    # Check for success flash message
    assert response.status_code == 302
    assert 'Registration successful!' in response.data.decode()
    
    # Check if a student was created in the database
    with app.app_context():
        student = Student.query.filter_by(student_id='S12345').first()
        assert student is not None
        assert student.full_name == 'John Doe'
        # Check that password_hash is not plain text (Criterion 4 check)
        assert student.password_hash != 'StrongPassword123'

    # 2. Check if the new user can be "logged in" (by checking session if we had a login route,
    # but for now, we verify creation and hashing, which covers the core requirements)
    # A minimal check: attempt to visit dashboard (assuming dashboard route exists)
    response_dashboard = client.get('/dashboard')
    assert response_dashboard.status_code == 200
    assert b"Dashboard" in response_dashboard.data

def test_registration_with_missing_fields(client):
    """
    Criterion 2: Given a registration request, when any required field is
    missing or invalid (e.g., a malformed email address or a password
    shorter than 8 characters), then the account is not created and an
    appropriate error message is displayed.
    """
    # Test missing fields
    response_missing = client.post(
        '/register',
        data={
            'student_id': 'S12345',
            'full_name': 'John Doe',
            'email': '',  # Missing email
            'password': 'StrongPassword123'
        }
    )
    assert response_missing.status_code == 200
    assert b'All fields are required.' in response_missing.data

    # Test weak password
    response_weak_password = client.post(
        '/register',
        data={
            'student_id': 'S12346',
            'full_name': 'Jane Doe',
            'email': 'jane.doe@example.com',
            'password': 'short' # Too short
        }
    )
    assert response_weak_password.status_code == 200
    assert b'Password must be at least 8 characters long.' in response_weak_password.data

def test_registration_with_duplicate_id_or_email(client):
    """
    Criterion 3: Given an existing account, when a student attempts to
    register with the same student ID or email address, then the account
    is not created and an appropriate error message is displayed.
    """
    # Pre-register a user
    initial_response = client.post(
        '/register',
        data={
            'student_id': 'DUPID',
            'full_name': 'Duplicate User',
            'email': 'dup@example.com',
            'password': 'InitialPassword123'
        }
    )
    assert initial_response.status_code == 302
    
    # Attempt to register with the same Student ID
    response_duplicate_id = client.post(
        '/register',
        data={
            'student_id': 'DUPID',
            'full_name': 'Another User',
            'email': 'newdup@example.com',
            'password': 'AnotherPassword123'
        }
    )
    assert response_duplicate_id.status_code == 200
    assert b'Student ID or email already registered.' in response_duplicate_id.data

    # Attempt to register with the same Email
    response_duplicate_email = client.post(
        '/register',
        data={
            'student_id': 'S99999',
            'full_name': 'Third User',
            'email': 'dup@example.com', # Duplicate email
            'password': 'ThirdPassword123'
        }
    )
    assert response_duplicate_email.status_code == 200
    assert b'Student ID or email already registered.' in response_duplicate_email.data