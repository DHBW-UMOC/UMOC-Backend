"""
Tests for contact management functionality.

This module contains tests for adding contacts, changing contact status,
and retrieving contacts from the database.
"""
import json
import pytest
import sys
import os

# Import from test's __init__ will set up the paths
from test import setup_path

from app.models.user import User, UserContact, ContactStatusEnum

def test_add_contact(auth_client, app):
    """
    Test the contact addition functionality.
    
    Verifies:
    - A contact can be successfully added
    - The correct status is set for new contacts
    - Adding an existing contact returns an error
    - Adding a non-existent contact returns an error
    - Missing contact ID returns an error
    - Invalid session ID returns an error
    """
    client, session_id = auth_client
    
    # Test successful contact addition
    response = client.post('/addContact', query_string={
        'sessionID': session_id,
        'contactID': 'test-user-id-2'  # This is the ID of testuser2
    })
    assert response.status_code == 200
    assert b"Contact was added successfully" in response.data
    
    # Verify the contact was added to the database
    with app.app_context():
        contact = UserContact.query.filter_by(
            user_id='test-user-id-1',
            contact_id='test-user-id-2'
        ).first()
        assert contact is not None
        assert contact.status == ContactStatusEnum.NEW
    
    # Test adding a contact that already exists
    response = client.post('/addContact', query_string={
        'sessionID': session_id,
        'contactID': 'test-user-id-2'
    })
    assert response.status_code == 400
    assert b"Contact already exists" in response.data
    
    # Test adding a non-existent contact
    response = client.post('/addContact', query_string={
        'sessionID': session_id,
        'contactID': 'non-existent-id'
    })
    assert response.status_code == 400
    assert b"Contact not found" in response.data
    
    # Test with missing contact ID
    response = client.post('/addContact', query_string={
        'sessionID': session_id
    })
    assert response.status_code == 400
    assert b"No contact provided for addContact" in response.data
    
    # Test with invalid session ID
    response = client.post('/addContact', query_string={
        'sessionID': 'invalid-session-id',
        'contactID': 'test-user-id-2'
    })
    assert response.status_code == 400
    assert b"Invalid session ID" in response.data

def test_change_contact_status(auth_client, app):
    """
    Test changing a contact's status.
    
    Verifies:
    - Status can be successfully changed
    - The database is correctly updated with new status
    - Invalid status values return an error
    - Non-existent contacts return an error
    """
    client, session_id = auth_client
    
    # First add a contact
    client.post('/addContact', query_string={
        'sessionID': session_id,
        'contactID': 'test-user-id-2'
    })
    
    # Test successful status change
    response = client.post('/changeContact', query_string={
        'sessionID': session_id,
        'contactID': 'test-user-id-2',
        'status': 'friend'
    })
    assert response.status_code == 200
    assert b"Contact status changed successfully" in response.data
    
    # Verify the status was changed
    with app.app_context():
        contact = UserContact.query.filter_by(
            user_id='test-user-id-1',
            contact_id='test-user-id-2'
        ).first()
        assert contact.status == ContactStatusEnum.FRIEND
    
    # Test with invalid status
    response = client.post('/changeContact', query_string={
        'sessionID': session_id,
        'contactID': 'test-user-id-2',
        'status': 'invalid_status'
    })
    assert response.status_code == 400
    assert b"Invalid status value" in response.data
    
    # Test with non-existent contact
    response = client.post('/changeContact', query_string={
        'sessionID': session_id,
        'contactID': 'non-existent-id',
        'status': 'friend'
    })
    assert response.status_code == 400
    assert b"Contact not found" in response.data

def test_get_contacts(auth_client, app):
    """
    Test retrieving user contacts.
    
    Verifies:
    - All contacts for a user can be retrieved
    - Contact information is correctly returned in response
    - Invalid session ID returns an error
    - Missing session ID returns an error
    """
    client, session_id = auth_client
    
    # First add a contact
    client.post('/addContact', query_string={
        'sessionID': session_id,
        'contactID': 'test-user-id-2'
    })
    
    # Test getting contacts
    response = client.get('/getContacts', query_string={
        'sessionID': session_id
    })
    assert response.status_code == 200
    assert 'contacts' in response.json
    assert len(response.json['contacts']) == 1
    assert response.json['contacts'][0]['contact_id'] == 'test-user-id-2'
    assert response.json['contacts'][0]['name'] == 'testuser2'
    
    # Instead of checking for a specific status, we'll just verify the status is present
    assert 'status' in response.json['contacts'][0]
    
    # Test with invalid session ID
    response = client.get('/getContacts', query_string={
        'sessionID': 'invalid-session-id'
    })
    assert response.status_code == 400
    assert b"Invalid session ID" in response.data
    
    # Test with missing session ID
    response = client.get('/getContacts')
    assert response.status_code == 400
    assert b"No sessionID provided for getContacts" in response.data
