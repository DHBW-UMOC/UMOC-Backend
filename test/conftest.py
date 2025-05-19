# Import compatibility patch first to fix collections issue
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Apply compatibility patch
from test.compatibility_patch import *

import pytest
# Update import to create or access the Flask app correctly
from app import create_app, db  # Try importing create_app directly from app

@pytest.fixture
def app():
    """Create application for the tests."""
    # Create the Flask app if it needs to be created
    flask_app = create_app()  # This uses the create_app function if available
    
    flask_app.config.update(
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        TESTING=True,
        DEBUG=False,
        WTF_CSRF_ENABLED=False
    )
    
    # Create the database and the database tables
    with flask_app.app_context():
        db.create_all()
    
    yield flask_app
    
    # Drop the database tables
    with flask_app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test CLI runner for the app."""
    return app.test_cli_runner()
