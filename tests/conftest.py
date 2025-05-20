import pytest
import os
from app import create_app, db
from app.models import User, MenuItem, Order, OrderItem
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Use in-memory SQLite for tests
    WTF_CSRF_ENABLED = False # Disable CSRF for easier form testing in client
    SECRET_KEY = 'test-secret-key' # Use a fixed key for tests
    SERVER_NAME = 'localhost.test' # Required for url_for in tests outside request context
    SESSION_COOKIE_HTTPONLY = False # Allow accessing session cookie in tests if needed
    SESSION_COOKIE_SECURE = False # Allow session cookie over HTTP for tests
    # Ensure Stripe keys are set, even if dummy values for tests not hitting Stripe API directly
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY') or 'sk_test_dummy'
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY') or 'pk_test_dummy'


@pytest.fixture(scope='session')
def app():
    """Creates a Flask application instance for the test session."""
    app = create_app(TestConfig)
    # Establish an application context before creating the DB tables
    app_context = app.app_context()
    app_context.push()

    # Create the database tables
    db.create_all()

    yield app # Provide the app instance to tests

    # Teardown: remove the context and drop tables
    db.session.remove()
    db.drop_all()
    app_context.pop()


@pytest.fixture(scope='function') # Use 'function' scope for client to get clean state per test
def client(app):
    """Creates a test client for the Flask application."""
    with app.test_client() as client:
        yield client
    # Context manager ensures proper cleanup


@pytest.fixture(scope='function')
def runner(app):
    """Creates a test command runner for the Flask application."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def init_database(app):
    """Fixture to handle database setup and teardown for each test function."""
    # Create the database tables (redundant if app fixture does it, but ensures clean state)
    # db.create_all() # Already done in app fixture

    yield db # Provide the db session to tests

    # Teardown: Ensure a completely clean database state for each test function
    # Remove the session first
    db.session.remove()
    # Drop all tables
    db.drop_all()
    # Recreate all tables for the next test
    # Need app context again for create_all
    with app.app_context():
        db.create_all()


from flask import url_for # Keep import


@pytest.fixture(scope='function')
def new_user(init_database): # Removed client dependency
    """Fixture to create a new user in the database for tests."""
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    # Let tests handle login if required
    yield user # Provide the user object to the test
    # No teardown needed here, client and db fixtures handle cleanup

# @pytest.fixture(scope='function') # Removing this fixture
# def logged_in_client(client, new_user):
#     """Fixture to provide a test client logged in as the new_user."""
#     # Log the user in using the test client
#     client.post('/auth/login', data={
#         'username': new_user.username,
#         'password': 'password'
#     }, follow_redirects=True)
#     yield client
#     # Log out after the test
#     client.get('/auth/logout', follow_redirects=True)


@pytest.fixture(scope='function')
def sample_menu_item(init_database):
    """Fixture to create a sample menu item."""
    item = MenuItem(name='Test Pizza', description='A delicious test pizza', price=12.99, category='Main Course')
    db.session.add(item)
    db.session.commit()
    return item
