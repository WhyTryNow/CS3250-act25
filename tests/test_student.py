import pytest
from app import create_app
from app.models import Student
from app.routes import student_bp

@pytest.fixture
def app():
    """Fixture for creating a test app."""
    app = create_app(config={'TESTING': True})
    yield app
    app.db.drop_all()

@pytest.fixture
def client(app):
    """Fixture for the test client."""
    return app.test_client()

@pytest.fixture
def db_session(app):
    """Fixture for a clean session before each test."""
    with app.app_context():
        db = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', 'sqlite:///:memory:')
        app.db.init_app(app) # Re-initialize db for testing context if necessary, though create_app handles it.
        yield app.db
        app.db.drop_all()

def test_successful_registration(client, db_session):
    """
    AC 1: Given an unregistered student, when the student submits valid data, 
    then a new student account is created.
    """
    student_data = {
        'student_id': 'S12345',
        'full_name': 'John Doe',
        'email': 'john.doe@example.com',
        'password': 'StrongPassword123'
    }
    response = client.post('/register', data=student_data)
    
    # Check for success message (implied by redirect to dashboard or a success flash)
    assert response.status_code == 200
    assert b'Registration successful!' in response.data
    
    # Verify creation in DB
    student = Student.query.filter_by(student_id='S12345').first()
    assert student is not None
    assert student.full_name == 'John Doe'
    # Verify password hashing (AC 4)
    assert student.password_hash != 'StrongPassword123'
    assert student.check_password('StrongPassword123') is True

def test_registration_missing_fields(client):
    """
    AC 2: Given a registration request, when any required field is missing, 
    then the account is not created and an error message is displayed.
    """
    # Test missing password
    data = {
        'student_id': 'S12345',
        'full_name': 'John Doe',
        'email': 'john.doe@example.com',
        'password': ''
    }
    response = client.post('/register', data=data)
    assert response.status_code == 200
    assert b'All fields are required.' in response.data
    
    # Test missing student_id
    data_no_id = {
        'full_name': 'John Doe',
        'email': 'john.doe@example.com',
        'password': 'ValidPass123'
    }
    response_no_id = client.post('/register', data=data_no_id)
    assert response_no_id.status_code == 200
    assert b'All fields are required.' in response_no_id.data

def test_registration_invalid_password_length(client):
    """
    AC 2: Given a registration request, when the password is shorter than 8 characters, 
    then the account is not created and an error message is displayed.
    """
    data = {
        'student_id': 'S12345',
        'full_name': 'John Doe',
        'email': 'john.doe@example.com',
        'password': 'short' # Length < 8
    }
    response = client.post('/register', data=data)
    assert response.status_code == 200
    assert b'Password must be at least 8 characters long.' in response.data
    
    # Ensure no student was created
    student = Student.query.filter_by(student_id='S12345').first()
    assert student is None


def test_registration_duplicate_student_id(client, db_session):
    """
    AC 3: Given an existing account, when a student attempts to register 
    with the same student ID, then the account is not created and an error message is displayed.
    """
    # 1. Register the first student successfully
    valid_data = {
        'student_id': 'DUP_ID_1',
        'full_name': 'Alice Smith',
        'email': 'alice1@test.com',
        'password': 'Pass12345'
    }
    client.post('/register', data=valid_data)
    
    # 2. Attempt to register with the same student ID
    duplicate_data = {
        'student_id': 'DUP_ID_1', # Duplicate ID
        'full_name': 'Alice Duplicate',
        'email': 'alice2@test.com', # Different email
        'password': 'AnotherPass!'
    }
    response = client.post('/register', data=duplicate_data)
    
    assert response.status_code == 200
    assert b'Student ID or email already registered.' in response.data
    
    # Verify only one student exists
    student_count = Student.query.count()
    assert student_count == 1

def test_registration_duplicate_email(client, db_session):
    """
    AC 3: Given an existing account, when a student attempts to register 
    with the same email address, then the account is not created and an error message is displayed.
    """
    # 1. Register the first student successfully
    valid_data = {
        'student_id': 'S_EMAIL_DUP',
        'full_name': 'Bob Johnson',
        'email': 'bob@duplicate.com',
        'password': 'Pass45678'
    }
    client.post('/register', data=valid_data)
    
    # 2. Attempt to register with the same email address
    duplicate_data = {
        'student_id': 'S_NEW_ID', # Different ID
        'full_name': 'Bob Duplicate',
        'email': 'bob@duplicate.com', # Duplicate Email
        'password': 'NewPass!'
    }
    response = client.post('/register', data=duplicate_data)
    
    assert response.status_code == 200
    assert b'Student ID or email already registered.' in response.data
    
    # Verify only one student exists
    student_count = Student.query.count()
    assert student_count == 1