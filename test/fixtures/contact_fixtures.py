"""
Common fixtures for contact-related tests
"""
import pytest
from app.models.user import UserContact, ContactStatusEnum

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
