import pytest
from app import create_app
from app.models import Student

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
        # Use in-memory SQLite for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.db.init_app(app)
        yield app.db
        app.db.drop_all()