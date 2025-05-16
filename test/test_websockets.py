import unittest
import uuid
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_socketio import SocketIOTestClient
import json
import time
import random
import string

from app import create_app
from app import db, socketio
from app.models.user import User, UserContact, ContactStatusEnum
from app.models.message import Message, MessageTypeEnum
from flask_jwt_extended import create_access_token

def generate_random_string(length=5):
    """Generate a random string for unique usernames"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

class WebSocketsTestCase(unittest.TestCase):
    def setUp(self):
        # Change how we create the testing app
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for tests
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Ensure clean database
        db.drop_all()
        db.create_all()
        
        # Generate unique usernames
        username1 = f"test_user_{generate_random_string()}"
        username2 = f"test_user_{generate_random_string()}"
        username3 = f"test_user_{generate_random_string()}"
        
        # Create test users with correct field names
        self.user1 = User(
            user_id=str(uuid.uuid4()),
            username=username1,
            is_online=False,
            salt='salt1',
            profile_picture="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png",
            created_at=None  # Let database set default timestamp
        )
        self.user1.password = 'test_hash_1'  # Try direct assignment
        
        self.user2 = User(
            user_id=str(uuid.uuid4()),
            username=username2,
            is_online=False,
            salt='salt2',
            profile_picture="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png",
            created_at=None
        )
        self.user2.password = 'test_hash_2'
        
        self.user3 = User(
            user_id=str(uuid.uuid4()),
            username=username3,
            is_online=False,
            salt='salt3',
            profile_picture="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png",
            created_at=None
        )
        self.user3.password = 'test_hash_3'
        
        db.session.add_all([self.user1, self.user2, self.user3])
        db.session.commit()
        
        # Create tokens for JWT authentication
        with self.app.app_context():
            self.token1 = create_access_token(identity=self.user1.user_id)
            self.token2 = create_access_token(identity=self.user2.user_id)
            self.token3 = create_access_token(identity=self.user3.user_id)
        
        # Create contacts
        contact1 = UserContact(
            user_id=self.user1.user_id,
            contact_id=self.user2.user_id,
            status=ContactStatusEnum.FRIEND,
            streak=0,
            continue_streak=True
        )
        contact2 = UserContact(
            user_id=self.user2.user_id,
            contact_id=self.user1.user_id,
            status=ContactStatusEnum.FRIEND,
            streak=0,
            continue_streak=True
        )
        
        db.session.add_all([contact1, contact2])
        db.session.commit()
        
        # Set up client
        self.client = self.app.test_client()
        
        # Clear user_sids dictionary and set up custom mock for request object
        from app.websocket import websockets
        websockets.user_sids = {}
        
        # Mock the request object directly in the websockets module
        self.mock_request = MagicMock()
        websockets.request = self.mock_request
        
        # Mock the verify_jwt_in_request function
        self.patcher = patch('app.websocket.websockets.verify_jwt_in_request')
        self.mock_verify_jwt = self.patcher.start()
        
    def tearDown(self):
        self.patcher.stop()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_connect_success(self):
        """Test successful WebSocket connection with valid JWT token"""
        # Set up test SID
        test_sid = f"test_sid_{generate_random_string()}"
        self.mock_request.sid = test_sid
        
        # Mock get_jwt_identity to return user1's ID and patch emit to prevent request context issues
        with patch('app.websocket.websockets.get_jwt_identity', return_value=self.user1.user_id), \
             patch('app.websocket.websockets.emit') as mock_emit:
            # Call connect handler directly
            from app.websocket.websockets import handle_connect, user_sids
            result = handle_connect()
            
            # Verify connection was successful
            self.assertTrue(result)
            
            # Check that user is marked as online
            user = User.query.filter_by(user_id=self.user1.user_id).first()
            self.assertTrue(user.is_online)
            
            # Verify user_sids dictionary is updated
            self.assertIn(self.user1.user_id, user_sids)
            self.assertEqual(user_sids[self.user1.user_id], test_sid)
    
    def test_connect_invalid_token(self):
        """Test connection rejection for invalid JWT token"""
        # Make verify_jwt_in_request raise an exception
        self.mock_verify_jwt.side_effect = Exception("Invalid token")
        
        # Call connect handler directly
        from app.websocket.websockets import handle_connect
        result = handle_connect()
        
        # Should reject the connection
        self.assertFalse(result)
    
    def test_disconnect(self):
        """Test WebSocket disconnection functionality"""
        # Set up test SID
        test_sid = f"test_sid_{generate_random_string()}"
        self.mock_request.sid = test_sid
        
        with patch('app.websocket.websockets.get_jwt_identity', return_value=self.user1.user_id):
            # Register user in user_sids
            from app.websocket.websockets import user_sids
            user_sids[self.user1.user_id] = test_sid
            
            # Set user as online
            user = User.query.filter_by(user_id=self.user1.user_id).first()
            user.is_online = True
            db.session.commit()
            
            # Call disconnect handler
            from app.websocket.websockets import handle_disconnect
            handle_disconnect()
            
            # Check that user is marked as offline
            user = User.query.filter_by(user_id=self.user1.user_id).first()
            self.assertFalse(user.is_online)
            
            # User should be removed from user_sids
            self.assertNotIn(self.user1.user_id, user_sids)
    
    def test_action_typing(self):
        """Test sending a typing action"""
        # Set up test SIDs
        test_sid1 = f"test_sid_{generate_random_string()}"
        test_sid2 = f"test_sid_{generate_random_string()}"
        self.mock_request.sid = test_sid1
        
        with patch('app.websocket.websockets.get_jwt_identity', return_value=self.user1.user_id):
            # Register users in user_sids
            from app.websocket.websockets import user_sids
            user_sids[self.user1.user_id] = test_sid1
            user_sids[self.user2.user_id] = test_sid2
            
            # Mock emit to capture calls
            with patch('app.websocket.websockets.emit') as mock_emit:
                # Create typing data
                data = {
                    'action': 'typing',
                    'data': {
                        'recipient_id': self.user2.user_id,
                        'char': 'H',
                        'is_group': False
                    }
                }
                
                # Call action handler directly
                from app.websocket.websockets import handle_action
                handle_action(data)
                
                # Verify emit was called with correct parameters
                mock_emit.assert_called_once()
                args, kwargs = mock_emit.call_args
                
                # Check event name and payload
                event_name = args[0]
                payload = args[1]
                self.assertEqual(event_name, 'typing')
                self.assertEqual(payload['sender_id'], self.user1.user_id)
                self.assertEqual(payload['char'], 'H')
                self.assertEqual(kwargs['room'], test_sid2)
    
    def test_action_send_message(self):
        """Test sending a message via action handler"""
        # Set up test SIDs
        test_sid1 = f"test_sid_{generate_random_string()}"
        test_sid2 = f"test_sid_{generate_random_string()}"
        self.mock_request.sid = test_sid1
        
        with patch('app.websocket.websockets.get_jwt_identity', return_value=self.user1.user_id):
            # Register users in user_sids
            from app.websocket.websockets import user_sids
            user_sids[self.user1.user_id] = test_sid1
            user_sids[self.user2.user_id] = test_sid2
            
            # Mock emit to capture calls
            with patch('app.websocket.websockets.emit') as mock_emit:
                # Create message data
                data = {
                    'action': 'sendMessage',
                    'data': {
                        'recipient_id': self.user2.user_id,
                        'content': 'Message via action handler',
                        'is_group': False,
                        'type': 'text'
                    }
                }
                
                # Call action handler directly
                from app.websocket.websockets import handle_action
                handle_action(data)
                
                # Verify emit was called with correct parameters
                mock_emit.assert_called_once()
                args, kwargs = mock_emit.call_args
                
                # Check event name and payload
                event_name = args[0]
                payload = args[1]
                self.assertEqual(event_name, 'new_message')
                self.assertEqual(payload['sender_id'], self.user1.user_id)
                self.assertEqual(payload['content'], 'Message via action handler')
                self.assertEqual(kwargs['room'], test_sid2)
                
                # Check if message was saved to database
                messages = Message.query.filter_by(
                    sender_user_id=self.user1.user_id,
                    recipient_user_id=self.user2.user_id,
                    encrypted_content='Message via action handler'
                ).all()
                self.assertEqual(len(messages), 1)
    
    def test_multiple_connections(self):
        """Test multiple connections from the same user"""
        # Set up test SIDs
        test_sid1 = f"test_sid_{generate_random_string()}"
        test_sid2 = f"test_sid_{generate_random_string()}"
        
        with patch('app.websocket.websockets.get_jwt_identity', return_value=self.user1.user_id):
            # First connection
            self.mock_request.sid = test_sid1
            from app.websocket.websockets import handle_connect, user_sids
            handle_connect()
            
            # Check that user is in user_sids with first SID
            self.assertIn(self.user1.user_id, user_sids)
            self.assertEqual(user_sids[self.user1.user_id], test_sid1)
            
            # Second connection
            self.mock_request.sid = test_sid2
            handle_connect()
            
            # Check that user is now in user_sids with second SID
            self.assertIn(self.user1.user_id, user_sids)
            self.assertEqual(user_sids[self.user1.user_id], test_sid2)
    
if __name__ == '__main__':
    unittest.main()
