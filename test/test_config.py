"""
Configuration for tests - centralizes test-specific settings
"""
import os

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
