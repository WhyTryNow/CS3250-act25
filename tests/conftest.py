import pytest
from app import create_app
from app.models import db, User, Course

@pytest.fixture(scope='function')
def app():
    # Create and configure app
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
    yield app

@pytest.fixture(scope='function')
def client(app):
    # Configures the test client
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def test_user(app):
    # Setup a test user
    with app.app_context():
        # Using a dummy hash for simplicity since we aren't hitting a real DB user creation path that sets the hash initially
        user = User(username='testuser', password_hash='fake_hash') 
        user.set_password('password123') 
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture(scope='function')
def course_data(test_user):
    # Setup a course for the user
    with app.app_context():
        course1 = Course(title='Calculus I', description='Intro to Calculus', gpa=4.0, is_completed=True, student_id=test_user.id)
        course2 = Course(title='Physics 101', description='Intro to Physics', gpa=3.5, is_completed=False, student_id=test_user.id)
        db.session.add_all([course1, course2])
        db.session.commit()
        return course1, course2