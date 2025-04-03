"""
Common fixtures for message-related tests
"""
import pytest
from app.models.message import Message

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
