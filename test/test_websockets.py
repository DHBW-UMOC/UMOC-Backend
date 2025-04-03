"""
Tests for WebSocket communication.

This module contains tests for real-time communication features
including establishing connections, sending messages, and adding
contacts through WebSocket channels.
"""
import pytest
import json
import time
import sys
import os

# Import from test's __init__ will set up the paths
from test import setup_path

from flask_socketio import SocketIOTestClient
from app.extensions import socketio, db
from app.models.user import User, UserContact, ContactStatusEnum
from app.models.message import Message, MessageTypeEnum

@pytest.fixture
def socket_client(app, auth_client):
    """
    Fixture providing a Socket.IO test client.
    
    Creates and configures a SocketIO test client with an authenticated
    session, and ensures proper cleanup after tests.
    """
    client, session_id = auth_client
    
    # Set up the socket client with the authenticated session
    socket_client = SocketIOTestClient(
        app,
        socketio,
        query_string=f'sessionID={session_id}'
    )
    yield socket_client, session_id
    socket_client.disconnect()

def test_socket_connection(socket_client, app):
    """
    Test WebSocket connection authentication.
    
    Verifies:
    - Authenticated clients can connect successfully
    - User is marked as online when connected
    - Unauthenticated clients are rejected
    """
    client, session_id = socket_client
    
    # Verify the client is connected
    assert client.is_connected()
    
    # Verify the user is marked as online
    with app.app_context():
        user = User.query.filter_by(user_id='test-user-id-1').first()
        assert user.is_online is True
    
    # Try to connect with invalid session ID
    invalid_client = SocketIOTestClient(
        app,
        socketio,
        query_string='sessionID=invalid-session-id'
    )
    assert not invalid_client.is_connected()

def test_send_message(socket_client, app):
    """
    Test sending messages through WebSocket.
    
    Verifies:
    - Messages can be sent through WebSocket
    - Messages are correctly saved in the database
    - The proper event is emitted to the recipient
    - Message data is correctly formatted
    
    This test handles existing contact relationships to prevent
    database constraint violations.
    """
    client, session_id = socket_client
    
    # Set up the contact relationship
    with app.app_context():
        # First check if the contact relationship already exists
        existing_contact = UserContact.query.filter_by(
            user_id='test-user-id-1',
            contact_id='test-user-id-2'
        ).first()
        
        if not existing_contact:
            contact = UserContact(
                user_id='test-user-id-1',
                contact_id='test-user-id-2',
                status=ContactStatusEnum.FRIEND
            )
            db.session.add(contact)
            db.session.commit()
    
    # Send a message
    client.emit('send_message', {
        'sessionID': session_id,
        'recipient_id': 'test-user-id-2',
        'content': 'Hello via socket',
        'type': 'text',
        'is_group': False
    })
    
    # Wait for the message to be processed
    time.sleep(0.1)
    
    # Check if the message was saved in the database
    with app.app_context():
        message = Message.query.filter_by(
            sender_user_id='test-user-id-1',
            recipient_user_id='test-user-id-2',
            encrypted_content='Hello via socket'
        ).first()
        assert message is not None
    
    # Verify that the client received the 'new_message' event
    received = client.get_received()
    assert len(received) > 0
    
    # Find the 'new_message' event
    new_message_events = [
        event for event in received 
        if event['name'] == 'new_message'
    ]
    assert len(new_message_events) > 0
    
    # Verify the message data
    message_data = new_message_events[0]['args'][0]
    assert message_data['sender_id'] == 'test-user-id-1'
    assert message_data['content'] == 'Hello via socket'
    assert message_data['type'] == 'text'
    assert message_data['is_group'] is False

def test_add_contact_socket(socket_client, app):
    """
    Test adding contacts through WebSocket.
    
    Verifies:
    - Contacts can be added through WebSocket
    - New contacts are properly stored in the database
    - The proper events are emitted to the client
    - Adding non-existent contacts returns an error
    
    This test ensures a clean state by removing any existing
    contact relationship before running the test.
    """
    client, session_id = socket_client
    
    # First, ensure the contact doesn't exist (clean up from previous tests)
    with app.app_context():
        existing_contact = UserContact.query.filter_by(
            user_id='test-user-id-1',
            contact_id='test-user-id-2'
        ).first()
        
        if existing_contact:
            db.session.delete(existing_contact)
            db.session.commit()
    
    # Add a contact
    client.emit('add_contact', {
        'sessionID': session_id,
        'contact_username': 'testuser2'
    })
    
    # Wait for the contact to be added
    time.sleep(0.1)
    
    # Verify the contact was added to the database
    with app.app_context():
        contact = UserContact.query.filter_by(
            user_id='test-user-id-1',
            contact_id='test-user-id-2'
        ).first()
        assert contact is not None
        # Verify status is NEW (since we're adding a fresh contact)
        assert contact.status == ContactStatusEnum.NEW
    
    # Verify that the client received the 'contact_added' event
    received = client.get_received()
    contact_added_events = [
        event for event in received 
        if event['name'] == 'contact_added'
    ]
    assert len(contact_added_events) > 0
    
    # Verify the contact data
    contact_data = contact_added_events[0]['args'][0]
    assert contact_data['user_id'] == 'test-user-id-2'
    assert contact_data['username'] == 'testuser2'
    assert contact_data['status'] == 'new'
    
    # Test adding a non-existent contact
    client.emit('add_contact', {
        'sessionID': session_id,
        'contact_username': 'nonexistent'
    })
    
    # Wait for the response
    time.sleep(0.1)
    
    # Verify that the client received an error event
    received = client.get_received()
    error_events = [
        event for event in received 
        if event['name'] == 'error'
    ]
    assert len(error_events) > 0
    assert 'User not found' in error_events[0]['args'][0]['message']
