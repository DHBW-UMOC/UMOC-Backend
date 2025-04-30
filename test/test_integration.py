# Import compatibility patch first to fix collections issue
from test.compatibility_patch import *

import json
import unittest
import pytest
from flask import request
from flask_testing import TestCase

# Update import to match conftest.py
from src.app import create_app, db

class BaseTestCase(TestCase):
    """Base test case class for all integration tests"""
    
    def create_app(self):
        """Required method for Flask-Testing"""
        # Create a Flask app instance using create_app
        app = create_app()
        app.config.update(
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            TESTING=True,
            DEBUG=False,
            WTF_CSRF_ENABLED=False
        )
        return app
    
    def setUp(self):
        """Set up test data"""
        db.create_all()
        
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()

    def print_routes(self):
        """Helper method to print available routes for debugging"""
        print("\n=== Available Application Routes ===")
        routes = []
        for rule in self.app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods))
            routes.append(f"{rule} - {rule.endpoint} - [{methods}]")
        
        # Sort routes for better readability
        for route in sorted(routes):
            print(route)
        print("===================================")


class TestApiEndpoints(BaseTestCase):
    """Integration tests for the actual API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        super().setUp()
        self.test_username = "testuser"
        self.test_password = "password123"
        self.test_user2 = "contact_user"
        self.test_password2 = "contact_pass"
        
        # Print available routes at the start of testing to help with debugging
        self.print_routes()
        
        # Note: Looking at the available routes, the API blueprint (api_bp) 
        # is registered without a URL prefix, so we access endpoints directly
        # without the '/api' prefix

    def debug_response(self, response, endpoint):
        """Helper to print debug information for a response"""
        print(f"\n=== Debugging {endpoint} ===")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Data: {response.data.decode('utf-8')}")
        print("==========================")
    
    def register_test_user(self, username=None, password=None):
        """Helper to register a test user"""
        username = username or self.test_username
        password = password or self.test_password
        return self.client.post(f'/register?username={username}&password={password}')
        
    def login_user(self, username=None, password=None):
        """Helper to log in a user and get auth headers"""
        username = username or self.test_username
        password = password or self.test_password
        response = self.client.get(f'/login?username={username}&password={password}')
        
        if response.status_code == 200:
            data = json.loads(response.data.decode('utf-8'))
            token = data['access_token']
            return {'Authorization': f'Bearer {token}'}, data
        return None, None
    
    def setup_users_and_login(self):
        """Helper to set up two users and get authentication for the first one"""
        # Register users
        self.register_test_user(self.test_username, self.test_password)
        self.register_test_user(self.test_user2, self.test_password2)
        
        # Login with first user
        headers, login_data = self.login_user(self.test_username, self.test_password)
        return headers, login_data
    
    def add_contact(self, headers):
        """Helper to add a contact and return the contact_id"""
        response = self.client.post(
            f'/addContact?contact_name={self.test_user2}',
            headers=headers
        )
        
        if response.status_code == 201:
            # Get contact ID from getContacts
            get_response = self.client.get('/getContacts', headers=headers)
            if get_response.status_code == 200:
                data = json.loads(get_response.data.decode('utf-8'))
                if data['contacts'] and len(data['contacts']) > 0:
                    return data['contacts'][0]['contact_id']
        return None
    
    # Individual endpoint tests
    
    def test_endpoint_register(self):
        """Test the register endpoint"""
        # Test successful registration
        response = self.client.post(
            f'/register?username={self.test_username}&password={self.test_password}'
        )
        if response.status_code != 201:
            self.debug_response(response, '/register')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('success', data)
        
        # Test duplicate username
        response = self.client.post(
            f'/register?username={self.test_username}&password={self.test_password}'
        )
        if response.status_code != 409:
            self.debug_response(response, '/register')
        self.assertEqual(response.status_code, 409)  # Conflict
        
        # Test invalid username format
        response = self.client.post(
            f'/register?username=invalid@user&password={self.test_password}'
        )
        if response.status_code != 400:
            self.debug_response(response, '/register')
        self.assertEqual(response.status_code, 400)
        
        # Test short username
        response = self.client.post(
            f'/register?username=ab&password={self.test_password}'
        )
        if response.status_code != 400:
            self.debug_response(response, '/register')
        self.assertEqual(response.status_code, 400)
    
    def test_endpoint_login(self):
        """Test the login endpoint"""
        # Register a user first
        self.register_test_user()
        
        # Test successful login
        response = self.client.get(
            f'/login?username={self.test_username}&password={self.test_password}'
        )
        if response.status_code != 200:
            self.debug_response(response, '/login')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('access_token', data)
        self.assertIn('user_id', data)
        
        # Test invalid credentials
        response = self.client.get(
            f'/login?username={self.test_username}&password=wrongpassword'
        )
        if response.status_code != 401:
            self.debug_response(response, '/login')
        self.assertEqual(response.status_code, 401)
    
    def test_endpoint_default(self):
        """Test the default endpoint (JWT protected)"""
        # Register and login to get auth token
        self.register_test_user()
        headers, data = self.login_user()
        
        # Test protected endpoint with valid token
        response = self.client.get('/', headers=headers)
        if response.status_code != 200:
            self.debug_response(response, '/')
        self.assertEqual(response.status_code, 200)
        
        # Test without auth headers - should fail
        response = self.client.get('/')
        if response.status_code not in [401, 422]:
            self.debug_response(response, '/')
        self.assertIn(response.status_code, [401, 422])
    
    def test_endpoint_logout(self):
        """Test the logout endpoint"""
        # Register and login to get auth token
        self.register_test_user()
        headers, data = self.login_user()
        
        # Test logout
        response = self.client.post('/logout', headers=headers)
        if response.status_code != 200:
            self.debug_response(response, '/logout')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('success', data)
    
    def test_endpoint_add_contact(self):
        """Test the addContact endpoint"""
        # Set up users and login
        headers, _ = self.setup_users_and_login()
        
        # Test adding a contact
        response = self.client.post(
            f'/addContact?contact_name={self.test_user2}',
            headers=headers
        )
        if response.status_code != 201:
            self.debug_response(response, '/addContact')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('success', data)
    
    def test_endpoint_get_chats(self):
        """Test the getContacts endpoint"""
        # Set up users, login, and add contact
        headers, _ = self.setup_users_and_login()
        self.client.post(
            f'/addContact?contact_name={self.test_user2}',
            headers=headers
        )
        
        # Test getting contacts
        response = self.client.get('/getChats', headers=headers)
        if response.status_code != 200:
            self.debug_response(response, '/getChats')
        self.assertEqual(response.status_code, 200)
    
    def test_endpoint_change_contact(self):
        """Test the changeContact endpoint"""
        # Set up users, login, and add contact
        headers, _ = self.setup_users_and_login()
        contact_id = self.add_contact(headers)
        
        # Check initial status using debugContacts
        debug_response = self.client.get('/debugContacts', headers=headers)
        debug_data = json.loads(debug_response.data.decode('utf-8'))
        initial_status = debug_data['contacts'][0]['status']
        
        print(f"\n=== Contact Debug Info for change_contact test ===")
        print(f"Initial status: {initial_status}")
        print(f"Contact ID: {contact_id}")
        
        # Use a valid status from ContactStatusEnum
        response = self.client.post(
            f'/changeContact?contact_id={contact_id}&status=friend',
            headers=headers
        )
        if response.status_code != 200:
            self.debug_response(response, '/changeContact')
        
        print(f"Change response: {response.status_code}")
        print(f"Response content: {response.data.decode('utf-8')}")
        
        # Assert the status code is 200 (success)
        self.assertEqual(response.status_code, 200)
        
        # Verify the status was changed
        debug_response = self.client.get('/debugContacts', headers=headers)
        debug_data = json.loads(debug_response.data.decode('utf-8'))
        updated_status = debug_data['contacts'][0]['status']
        self.assertEqual(updated_status, 'friend')
    
    def test_endpoint_debug_contacts(self):
        """Test the debugContacts endpoint"""
        # Set up users, login, and add contact
        headers, _ = self.setup_users_and_login()
        self.add_contact(headers)
        
        # Test debug endpoint
        response = self.client.get('/debugContacts', headers=headers)
        if response.status_code != 200:
            self.debug_response(response, '/debugContacts')
        self.assertEqual(response.status_code, 200)
        debug_data = json.loads(response.data.decode('utf-8'))
        
        # Verify debug data
        self.assertEqual(debug_data['username'], self.test_username)
        self.assertEqual(debug_data['contact_count'], 1)
        self.assertTrue(len(debug_data['contacts']) > 0)
    
    def test_endpoint_save_message(self):
        """Test the saveMessage endpoint"""
        # Set up users, login, and add contact
        headers, _ = self.setup_users_and_login()
        contact_id = self.add_contact(headers)
        
        # Test saving a message
        message_content = "Hello, this is a test message!"
        response = self.client.post(
            '/saveMessage',
            json={
                'recipient_id': contact_id,
                'content': message_content,
                'is_group': False
            },
            headers=headers
        )
        if response.status_code != 200:
            self.debug_response(response, '/saveMessage')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('success', data)
    
    def test_endpoint_get_contact_messages(self):
        """Test the getContactMessages endpoint"""
        # Set up users, login, and add contact
        headers, _ = self.setup_users_and_login()
        contact_id = self.add_contact(headers)
        
        # Send a test message first
        message_content = "Hello, this is a test message!"
        self.client.post(
            '/saveMessage',
            json={
                'recipient_id': contact_id,
                'content': message_content,
                'is_group': False
            },
            headers=headers
        )
        
        # Test getting messages
        response = self.client.get(
            f'/getContactMessages?contact_id={contact_id}',
            headers=headers
        )
        if response.status_code != 200:
            self.debug_response(response, '/getContactMessages')
        self.assertEqual(response.status_code, 200)
        messages_data = json.loads(response.data.decode('utf-8'))
        self.assertTrue('messages' in messages_data)
        self.assertTrue(len(messages_data['messages']) > 0)
        self.assertEqual(messages_data['messages'][0]['content'], message_content)

    def test_endpoint_get_groups(self):
        """Test the getGroups endpoint"""
        # Set up users and login
        headers, _ = self.setup_users_and_login()

        # Test getting groups
        response = self.client.get('/getGroups', headers=headers)
        if response.status_code != 200:
            self.debug_response(response, '/getGroups')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('groups', data)
        self.assertTrue(len(data['groups']) >= 0)

    def test_endpoint_create_group(self):
        """Test the createGroup endpoint"""
        # Set up users and login
        headers, _ = self.setup_users_and_login()

        # Test creating a group
        group_name = "Test Group"
        response = self.client.post(
            f'/createGroup?group_name={group_name}',
            headers=headers
        )
        if response.status_code != 201:
            self.debug_response(response, '/createGroup')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('success', data)

        self.assertIn('group_id', data)
        self.assertIn('group_name', data)
        self.assertEqual(data['group_name'], group_name)
        self.assertIn('admin_user_id', data)

    def test_endpoint_delete_group(self):
        """Test the deleteGroup endpoint"""
        # Set up users and login
        headers, _ = self.setup_users_and_login()

        # Create a group first
        group_name = "Test Group"
        response = self.client.post(
            f'/createGroup?group_name={group_name}',
            headers=headers
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        group_id = data['group_id']

        # Test deleting the group
        response = self.client.post(
            f'/deleteGroup?group_id={group_id}',
            headers=headers
        )
        if response.status_code != 200:
            self.debug_response(response, '/deleteGroup')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('success', data)

    def test_endpoint_change_group_name(self):
        """Test the changeGroupName endpoint"""
        # Set up users and login
        headers, _ = self.setup_users_and_login()

        # Create a group first
        group_name = "Test Group"
        response = self.client.post(
            f'/createGroup?group_name={group_name}',
            headers=headers
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        group_id = data['group_id']

        # Test changing the group name
        new_group_name = "Updated Group Name"
        response = self.client.post(
            f'/changeGroupName?group_id={group_id}&new_name={new_group_name}',
            headers=headers
        )
        if response.status_code != 200:
            self.debug_response(response, '/changeGroupName')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('success', data)

    def test_endpoint_change_group_picture(self):
        """Test the changeGroupPicture endpoint"""
        # Set up users and login
        headers, _ = self.setup_users_and_login()

        # Create a group first
        group_name = "Test Group"
        response = self.client.post(
            f'/createGroup?group_name={group_name}',
            headers=headers
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        group_id = data['group_id']

        # Test changing the group picture
        new_picture_url = "http://example.com/new_picture.jpg"
        response = self.client.post(
            f'/changeGroupPicture?group_id={group_id}&new_picture={new_picture_url}',
            headers=headers
        )
        if response.status_code != 200:
            self.debug_response(response, '/changeGroupPicture')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('success', data)

    def test_endpoint_change_group_admin(self):
        """Test the changeGroupAdmin endpoint"""
        # Set up users and login
        headers, _ = self.setup_users_and_login()

        # Create a group first
        group_name = "Test Group"
        response = self.client.post(
            f'/createGroup?group_name={group_name}',
            headers=headers
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        group_id = data['group_id']

        # Test changing the group admin
        new_admin_id = "new_admin_user_id"
        response = self.client.post(
            f'/changeGroupAdmin?group_id={group_id}&new_admin_id={new_admin_id}',
            headers=headers
        )
        if response.status_code != 200:
            self.debug_response(response, '/changeGroupAdmin')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('success', data)

    def test_endpoint_get_group_members(self):
        """Test the getGroupMembers endpoint"""
        # Set up users and login
        headers, _ = self.setup_users_and_login()

        # Create a group first
        group_name = "Test Group"
        response = self.client.post(
            f'/createGroup?group_name={group_name}',
            headers=headers
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        group_id = data['group_id']

        # Test getting group members
        response = self.client.get(
            f'/getGroupMembers?group_id={group_id}',
            headers=headers
        )
        if response.status_code != 200:
            self.debug_response(response, '/getGroupMembers')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('members', data)
        self.assertTrue(len(data['members']) >= 0)

    def test_endpoint_get_group_messages(self):
        """Test the getGroupMessages endpoint"""
        # Set up users and login
        headers, _ = self.setup_users_and_login()

        # Create a group first
        group_name = "Test Group"
        response = self.client.post(
            f'/createGroup?group_name={group_name}',
            headers=headers
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        group_id = data['group_id']

        # Test getting group messages
        response = self.client.get(
            f'/getGroupMessages?group_id={group_id}',
            headers=headers
        )
        if response.status_code != 200:
            self.debug_response(response, '/getGroupMessages')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('messages', data)
        self.assertTrue(len(data['messages']) >= 0)

    def test_add_group_member(self):
        """Test the addGroupMember endpoint"""
        # Set up users and login
        headers, _ = self.setup_users_and_login()

        # Create a group first
        group_name = "Test Group"
        response = self.client.post(
            f'/createGroup?group_name={group_name}',
            headers=headers
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        group_id = data['group_id']

        # Test adding a member to the group
        new_member_id = "new_member_user_id"
        response = self.client.post(
            f'/addGroupMember?group_id={group_id}&new_member_id={new_member_id}',
            headers=headers
        )
        if response.status_code != 200:
            self.debug_response(response, '/addGroupMember')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('success', data)

    def test_remove_group_member(self):
        """Test the removeGroupMember endpoint"""
        # Set up users and login
        headers, _ = self.setup_users_and_login()

        # Create a group first
        group_name = "Test Group"
        response = self.client.post(
            f'/createGroup?group_name={group_name}',
            headers=headers
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        group_id = data['group_id']

        # Test removing a member from the group
        member_id = "member_user_id"
        response = self.client.post(
            f'/removeGroupMember?group_id={group_id}&member_id={member_id}',
            headers=headers
        )
        if response.status_code != 200:
            self.debug_response(response, '/removeGroupMember')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('success', data)

    def test_send_message(self):
        """Test the sendMessage endpoint"""
        # Set up users and login
        headers, _ = self.setup_users_and_login()

        # Add a contact first
        contact_id = self.add_contact(headers)

        # Test sending a message
        message_content = "Hello, this is a test message!"
        response = self.client.post(
            '/sendMessage',
            json={
                'recipient_id': contact_id,
                'content': message_content,
                'is_group': False
            },
            headers=headers
        )
        if response.status_code != 200:
            self.debug_response(response, '/sendMessage')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('success', data)


if __name__ == '__main__':
    unittest.main()
