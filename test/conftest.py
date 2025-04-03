import os
import sys
import importlib.util
import pytest  # Add this import!

# Get the absolute paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(project_root, 'src')

# Force-add paths at the beginning of sys.path
if src_path in sys.path:
    sys.path.remove(src_path)  # Remove if exists
sys.path.insert(0, src_path)  # Add at the beginning

if project_root in sys.path:
    sys.path.remove(project_root)  # Remove if exists
sys.path.insert(0, project_root)  # Add at the beginning

print(f"Project root path: {project_root}")
print(f"Source path: {src_path}")
print(f"Current sys.path: {sys.path}")

# Import test configuration - this should be available regardless of import path success
from test.test_config import TEST_USERS

# Manually create a module spec and import modules from absolute paths
# This is a more reliable way to import modules when paths are problematic
def import_module_from_path(module_name, module_path):
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

# VS Code PyTest integration helper
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
