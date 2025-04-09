"""
Master configuration file for tests - consolidates all fixtures and test configuration
"""
import os
import sys
import importlib
import importlib.util
import pytest

# ----------------------------------------------------------------------
# Path and environment setup
# ----------------------------------------------------------------------

# Get the absolute paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(project_root, 'src')

# Force-add paths at the beginning of sys.path
if src_path in sys.path:
    sys.path.remove(src_path)
sys.path.insert(0, src_path)

if project_root in sys.path:
    sys.path.remove(project_root)
sys.path.insert(0, project_root)

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = os.pathsep.join([project_root, src_path])

print(f"Project root path: {project_root}")
print(f"Source path: {src_path}")
print(f"sys.path: {sys.path}")

# ----------------------------------------------------------------------
# Test configuration constants
# ----------------------------------------------------------------------

# Test database URI - use in-memory SQLite for tests
TEST_DATABASE_URI = 'sqlite:///:memory:'

# Test users
TEST_USERS = {
    'user1': {
        'user_id': 'test-user-id-1',
        'username': 'testuser1',
        'password': 'password1',
        'salt': 'test-salt',
        'public_key': 'test-public-key'
    },
    'user2': {
        'user_id': 'test-user-id-2',
        'username': 'testuser2',
        'password': 'password2',
        'salt': 'test-salt',
        'public_key': 'test-public-key'
    }
}

# Test API endpoint base URL
API_BASE_URL = 'http://127.0.0.1:5000'

# ----------------------------------------------------------------------
# Module imports
# ----------------------------------------------------------------------

def import_module_from_path(module_name, module_path):
    """Helper function to import modules from absolute paths"""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        print(f"Could not find module {module_name} at {module_path}")
        return None
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Check if modules are importable directly (normal case)
try:
    from app.extensions import db
    from app.config import TestConfig
    from app.models.user import User, UserContact, ContactStatusEnum
    from app.models.message import Message, MessageTypeEnum
    from app import create_app
    print("Successfully imported modules using normal imports")
except ImportError as e:
    print(f"Normal imports failed: {e}")
    
    # Try to manually import the required modules
    try:
        # Find the extension module
        extensions_path = os.path.join(src_path, 'app', 'extensions.py')
        ext_module = import_module_from_path('app.extensions', extensions_path)
        db = ext_module.db
        
        # Find the config module
        config_path = os.path.join(src_path, 'app', 'config.py')
        config_module = import_module_from_path('app.config', config_path)
        TestConfig = config_module.TestConfig
        
        # Find the user model module
        user_model_path = os.path.join(src_path, 'app', 'models', 'user.py')
        user_module = import_module_from_path('app.models.user', user_model_path)
        User = user_module.User
        UserContact = user_module.UserContact
        ContactStatusEnum = user_module.ContactStatusEnum
        
        # Find the message model module
        message_model_path = os.path.join(src_path, 'app', 'models', 'message.py')
        message_module = import_module_from_path('app.models.message', message_model_path)
        Message = message_module.Message
        MessageTypeEnum = message_module.MessageTypeEnum
        
        # Find the app module
        app_init_path = os.path.join(src_path, 'app', '__init__.py')
        app_module = import_module_from_path('app', app_init_path)
        create_app = app_module.create_app
        
        print("Successfully imported modules using manual import")
    except Exception as e:
        print(f"Manual import failed: {e}")
        raise

# ----------------------------------------------------------------------
# Pytest configuration and fixtures
# ----------------------------------------------------------------------

def pytest_configure(config):
    """Register custom markers to avoid warnings in VS Code."""
    config.addinivalue_line("markers", "unit: mark a test as a unit test")
    config.addinivalue_line("markers", "integration: mark a test as an integration test")
    config.addinivalue_line("markers", "api: mark a test as an API test")
    config.addinivalue_line("markers", "websocket: mark a test as a WebSocket test")

@pytest.fixture(scope='session')
def app():
    """Create and configure a Flask app for testing - reused across the test session."""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        
        # Insert test users from config
        test_users = []
        for user_data in TEST_USERS.values():
            test_user = User(
                user_id=user_data['user_id'],
                username=user_data['username'],
                password=user_data['password'],
                salt=user_data['salt'],
                public_key=user_data['public_key']
            )
            test_users.append(test_user)
        
        db.session.add_all(test_users)
        db.session.commit()
    
    yield app
    
    # Clean up after all tests
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers():
    """Authentication headers for test requests."""
    return {
        'username': TEST_USERS['user1']['username'],
        'password': TEST_USERS['user1']['password']
    }

@pytest.fixture
def auth_client(client, auth_headers):
    """A client with a valid session ID."""
    response = client.get('/login', query_string=auth_headers)
    session_id = response.json.get('sessionID')
    return client, session_id

@pytest.fixture
def db_session(app):
    """Provide a database session for tests that need direct DB access."""
    with app.app_context():
        yield db.session
        # Roll back changes made during the test
        db.session.rollback()

@pytest.fixture
def test_user_ids():
    """Return test user IDs from config for convenient access."""
    return {name: data['user_id'] for name, data in TEST_USERS.items()}

# ----------------------------------------------------------------------
# Contact fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def setup_contact(auth_client, app, test_user_ids):
    """Set up a contact relationship between test users."""
    client, session_id = auth_client
    
    # Add user2 as a contact for user1
    client.post('/addContact', query_string={
        'sessionID': session_id,
        'contactID': test_user_ids['user2']
    })
    
    # Return the client, session ID, and user IDs for convenience
    return {
        'client': client,
        'session_id': session_id,
        'user1_id': test_user_ids['user1'],
        'user2_id': test_user_ids['user2']
    }

@pytest.fixture
def setup_friend_contact(setup_contact, app):
    """Set up a contact relationship with FRIEND status."""
    client = setup_contact['client']
    session_id = setup_contact['session_id']
    user2_id = setup_contact['user2_id']
    
    # Change contact status to FRIEND
    client.post('/changeContact', query_string={
        'sessionID': session_id,
        'contactID': user2_id,
        'status': 'friend'
    })
    
    return setup_contact

# ----------------------------------------------------------------------
# Message fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def send_test_message(setup_contact, app):
    """Send a test message from user1 to user2."""
    client = setup_contact['client']
    session_id = setup_contact['session_id']
    user2_id = setup_contact['user2_id']
    
    message_content = 'Hello, this is a test message'
    
    # Send a message
    message_data = {
        'sessionID': session_id,
        'recipientID': user2_id,
        'content': message_content
    }
    
    response = client.post('/saveMessage', 
                         json=message_data,
                         content_type='application/json')
    
    setup_contact['message_content'] = message_content
    return setup_contact
