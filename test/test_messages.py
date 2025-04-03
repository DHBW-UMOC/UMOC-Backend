"""
Tests for messaging functionality.

This module contains tests for saving messages and retrieving
conversation history between contacts.
"""
import json
import pytest
import sys
import os

# Import from test's __init__ will set up the paths
from test import setup_path

from app.models.message import Message
from app.extensions import db  # Import db directly

def test_save_message(auth_client, app):
    """
    Test saving a message to the database.
    
    Verifies:
    - Messages can be successfully saved to the database
    - Message data is correctly stored
    - Invalid session ID returns an error
    - Non-existent recipient returns an error
    - Empty message content returns an error
    """
    client, session_id = auth_client
    
    # First add a contact
    client.post('/addContact', query_string={
        'sessionID': session_id,
        'contactID': 'test-user-id-2'
    })
    
    # Test successful message saving
    message_data = {
        'sessionID': session_id,
        'recipientID': 'test-user-id-2',
        'content': 'Hello, this is a test message'
    }
    response = client.post('/saveMessage', 
                          json=message_data,
                          content_type='application/json')
    assert response.status_code == 200
    assert b"Message saved successfully" in response.data
    
    # Verify the message was saved to the database
    with app.app_context():
        message = Message.query.filter_by(
            sender_user_id='test-user-id-1',
            recipient_user_id='test-user-id-2'
        ).first()
        assert message is not None
        assert message.encrypted_content == 'Hello, this is a test message'
    
    # Test with invalid session ID
    message_data['sessionID'] = 'invalid-session-id'
    response = client.post('/saveMessage', 
                          json=message_data,
                          content_type='application/json')
    assert response.status_code == 400
    assert b"Invalid session ID" in response.data
    
    # Test with non-existent recipient
    message_data['sessionID'] = session_id
    message_data['recipientID'] = 'non-existent-id'
    response = client.post('/saveMessage', 
                          json=message_data,
                          content_type='application/json')
    assert response.status_code == 400
    assert b"Recipient not found" in response.data
    
    # Test with missing content
    message_data['recipientID'] = 'test-user-id-2'
    message_data['content'] = ''
    response = client.post('/saveMessage', 
                          json=message_data,
                          content_type='application/json')
    assert response.status_code == 400
    assert b"No content provided for saveMessage" in response.data

def test_get_contact_messages(auth_client, app):
    """
    Test retrieving messages between contacts.
    
    Verifies:
    - Messages between two contacts can be retrieved
    - Message content and sender details are correctly returned
    - Proper filtering of messages to only show conversations 
      between the specified contacts
    - Invalid session ID returns an error
    - Non-existent contact returns an error
    - Missing contact ID returns an error
    
    This test ensures a clean state by removing existing messages
    between the test users before adding a new test message.
    """
    client, session_id = auth_client
    
    # Clean existing messages between the test users to ensure a clean state
    with app.app_context():
        Message.query.filter(
            ((Message.sender_user_id == 'test-user-id-1') & (Message.recipient_user_id == 'test-user-id-2')) |
            ((Message.sender_user_id == 'test-user-id-2') & (Message.recipient_user_id == 'test-user-id-1'))
        ).delete()
        db.session.commit()  # Use db.session instead of app.db.session
    
    # Setup: Add a contact and send a message
    client.post('/addContact', query_string={
        'sessionID': session_id,
        'contactID': 'test-user-id-2'
    })
    
    message_data = {
        'sessionID': session_id,
        'recipientID': 'test-user-id-2',
        'content': 'Hello, this is a test message'
    }
    client.post('/saveMessage', 
               json=message_data,
               content_type='application/json')
    
    # Test getting messages
    response = client.get('/getContactMessages', query_string={
        'sessionID': session_id,
        'contactID': 'test-user-id-2'
    })
    assert response.status_code == 200
    assert 'messages' in response.json
    assert len(response.json['messages']) == 1
    assert response.json['messages'][0]['content'] == 'Hello, this is a test message'
    assert response.json['messages'][0]['sender_user_id'] == 'test-user-id-1'
    
    # Test with invalid session ID
    response = client.get('/getContactMessages', query_string={
        'sessionID': 'invalid-session-id',
        'contactID': 'test-user-id-2'
    })
    assert response.status_code == 400
    assert b"Invalid session ID" in response.data
    
    # Test with non-existent contact
    response = client.get('/getContactMessages', query_string={
        'sessionID': session_id,
        'contactID': 'non-existent-id'
    })
    assert response.status_code == 400
    assert b"Contact not found" in response.data
    
    # Test with missing contact ID
    response = client.get('/getContactMessages', query_string={
        'sessionID': session_id
    })
    assert response.status_code == 400
    assert b"No contact provided for getContactMessages" in response.data
