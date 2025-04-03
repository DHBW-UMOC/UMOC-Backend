import json
import pytest
import sys
import os

# Import from test's __init__ will set up the paths
from test import setup_path

from app.models.user import User

def test_register_user(client):
    """Test user registration."""
    # Test successful registration
    response = client.post('/register', query_string={
        'username': 'newuser',
        'password': 'newpassword'
    })
    assert response.status_code == 200
    assert b"User registered successfully" in response.data
    
    # Test registration with an existing username
    response = client.post('/register', query_string={
        'username': 'testuser1',  # This username already exists
        'password': 'password'
    })
    assert response.status_code == 400
    assert b"Username already exists" in response.data
    
    # Test registration with missing username
    response = client.post('/register', query_string={
        'password': 'password'
    })
    assert response.status_code == 400
    assert b"No username provided for register" in response.data
    
    # Test registration with missing password
    response = client.post('/register', query_string={
        'username': 'user123'
    })
    assert response.status_code == 400
    assert b"No password provided for register" in response.data

def test_login_user(client, app):
    """Test user login."""
    # Test successful login
    response = client.get('/login', query_string={
        'username': 'testuser1',
        'password': 'password1'
    })
    assert response.status_code == 200
    assert 'sessionID' in response.json
    
    # Test login with invalid credentials
    response = client.get('/login', query_string={
        'username': 'testuser1',
        'password': 'wrongpassword'
    })
    assert response.status_code == 400
    assert b"Invalid username or password" in response.data
    
    # Test login with missing username
    response = client.get('/login', query_string={
        'password': 'password1'
    })
    assert response.status_code == 400
    assert b"No username provided for login" in response.data
    
    # Test login with missing password
    response = client.get('/login', query_string={
        'username': 'testuser1'
    })
    assert response.status_code == 400
    assert b"No password provided for login" in response.data
    
    # Verify that the user is marked as online after login
    with app.app_context():
        user = User.query.filter_by(username='testuser1').first()
        assert user.is_online is True

def test_logout_user(auth_client, app):
    """Test user logout."""
    client, session_id = auth_client
    
    # Test successful logout
    response = client.post('/logout', query_string={
        'sessionID': session_id
    })
    assert response.status_code == 200
    assert b"User logged out successfully" in response.data
    
    # Verify that the user is marked as offline after logout
    with app.app_context():
        user = User.query.filter_by(username='testuser1').first()
        assert user.session_id is None
        assert user.is_online is False
    
    # Test logout with invalid session ID
    response = client.post('/logout', query_string={
        'sessionID': 'invalid-session-id'
    })
    assert response.status_code == 400
    assert b"Invalid session ID" in response.data
    
    # Test logout with missing session ID
    response = client.post('/logout')
    assert response.status_code == 400
    assert b"No sessionID provided for logout" in response.data
