import pytest
from app import create_app
from app.models import Student
from app.routes import student_bp
from flask import url_for, session, redirect, request

@pytest.fixture
def app():
    """Create and configure a new app instance."""
    app = create_app()
    app.config['TESTING'] = True
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    with app.test_client() as client:
        yield client

@pytest.fixture
def db_setup(app):
    """Set up the database for testing (in-memory SQLite)."""
    with app.app_context():
        from app import db
        db.create_all()
        yield db

def test_successful_registration(client, db_setup):
    """
    Acceptance Criterion 1: Given an unregistered student, when the student submits
    student ID, full name, email address, and password, then a new student account
    is created and the student can log in with those credentials.
    """
    # 1. Register a new student
    response = client.post('/register', data={
        'student_id': 'S12345',
        'full_name': 'Test User',
        'email': 'test@example.com',
        'password': 'StrongPassword123'
    })

    assert response.status_code == 302
    # Check for success message
    assert b'Registration successful!' in response.data
    
    # 2. Verify student exists in DB
    with db_setup.session.get(Student, 1) as student: # Assuming it gets ID 1 after creation
        assert student is not None
        assert student.student_id == 'S12345'
        # AC 4 check (implicit): Password hash should be present, not plain text
        assert student.password_hash is not None
        assert not student.password_hash == 'StrongPassword123'

def test_registration_missing_fields(client, db_setup):
    """
    Acceptance Criterion 2: Given a registration request, when any required field is
    missing or invalid, then the account is not created and an appropriate error
    message is displayed.
    """
    # Submit with no data
    response = client.post('/register', data={})
    assert response.status_code == 200 # Should return to the form with an error flash

    # Submit with some data missing (e.g., password missing)
    response = client.post('/register', data={
        'student_id': 'S12345',
        'full_name': 'Test User',
        'email': 'test@example.com',
    })
    assert response.status_code == 200
    # Check for the 'All fields are required.' flash message
    assert b'All fields are required.' in response.data

def test_registration_invalid_password_length(client, db_setup):
    """
    Acceptance Criterion 2: Given a registration request, when a password shorter than 8
    characters is provided, then the account is not created and an appropriate error
    message is displayed.
    """
    response = client.post('/register', data={
        'student_id': 'S12345',
        'full_name': 'Test User',
        'email': 'test@example.com',
        'password': 'short' # Too short
    })
    assert response.status_code == 200
    # Check for password length error
    assert b'Password must be at least 8 characters long.' in response.data
    
    # Ensure no student was created
    with db_setup.session.query(Student).count() as count:
        assert count == 0

def test_registration_invalid_email_format(client, db_setup):
    """
    Acceptance Criterion 2: Given a registration request, when an invalid email address is
    provided, then the account is not created and an appropriate error message is displayed.
    """
    response = client.post('/register', data={
        'student_id': 'S12345',
        'full_name': 'Test User',
        'email': 'invalid-email', # Invalid format
        'password': 'StrongPassword123'
    })
    assert response.status_code == 200
    # Check for email format error
    assert b'Invalid email address format.' in response.data
    
    # Ensure no student was created
    with db_setup.session.query(Student).count() as count:
        assert count == 0

def test_registration_duplicate_student_id(client, db_setup):
    """
    Acceptance Criterion 3: Given an existing account, when a student attempts to
    register with the same student ID, then the account is not created and an
    appropriate error message is displayed.
    """
    # 1. Register a student first
    client.post('/register', data={
        'student_id': 'DUP_ID',
        'full_name': 'Original',
        'email': 'original@test.com',
        'password': 'OriginalPass123'
    })

    # 2. Attempt to register with the same ID
    response = client.post('/register', data={
        'student_id': 'DUP_ID',
        'full_name': 'Duplicate',
        'email': 'duplicate@test.com',
        'password': 'AnotherPass123'
    })
    assert response.status_code == 200
    # Check for duplicate error message
    assert b'Student ID or email already registered.' in response.data

    # Verify only one student exists
    with db_setup.session.query(Student).count() as count:
        assert count == 1

def test_registration_duplicate_email(client, db_setup):
    """
    Acceptance Criterion 3: Given an existing account, when a student attempts to
    register with the same email address, then the account is not created and an
    appropriate error message is displayed.
    """
    # 1. Register a student first
    client.post('/register', data={
        'student_id': 'S2',
        'full_name': 'Original',
        'email': 'existing@test.com',
        'password': 'OriginalPass123'
    })

    # 2. Attempt to register with the same email
    response = client.post('/register', data={
        'student_id': 'S3',
        'full_name': 'New User',
        'email': 'existing@test.com', # Duplicate email
        'password': 'NewPass123'
    })
    assert response.status_code == 200
    # Check for duplicate error message
    assert b'Student ID or email already registered.' in response.data

    # Verify only one student exists
    with db_setup.session.query(Student).count() as count:
        assert count == 1