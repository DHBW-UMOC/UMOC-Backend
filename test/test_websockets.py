import unittest
import uuid
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_socketio import SocketIOTestClient
import json
import time

from app import create_app
from app.extensions import db, socketio
from app.models.user import User, UserContact, ContactStatusEnum
from app.models.message import Message, MessageTypeEnum

class WebSocketsTestCase(unittest.TestCase):
    def setUp(self):
        # Change how we create the testing app
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test users with correct field names
        self.user1 = User(
            user_id=str(uuid.uuid4()),
            username='testuser1',
            # Remove password_hash field and use password instead or skip it
            # The field might be named differently or set through a method
            session_id=str(uuid.uuid4()),
            is_online=False
        )
        # Set password separately if there's a setter method
        self.user1.password = 'test_hash_1'  # Try direct assignment
        
        self.user2 = User(
            user_id=str(uuid.uuid4()),
            username='testuser2',
            session_id=str(uuid.uuid4()),
            is_online=False
        )
        self.user2.password = 'test_hash_2'
        
        self.user3 = User(
            user_id=str(uuid.uuid4()),
            username='testuser3',
            session_id=str(uuid.uuid4()),
            is_online=False
        )
        self.user3.password = 'test_hash_3'
        
        db.session.add_all([self.user1, self.user2, self.user3])
        db.session.commit()
        
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
        
        # Clear user_sids dictionary before each test
        from app.websocket.websockets import user_sids
        user_sids.clear()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_connect_success(self):
        """Test successful WebSocket connection"""
        client = socketio.test_client(self.app, query_string=f'sessionID={self.user1.session_id}')
        self.assertTrue(client.is_connected())
        
        # Check that user is marked as online
        user = User.query.get(self.user1.user_id)
        self.assertTrue(user.is_online)
        
        # Verify user_sids dictionary is updated
        from app.websocket.websockets import user_sids
        self.assertIn(self.user1.user_id, user_sids)
        
        # Disconnect
        client.disconnect()
    
    def test_connect_missing_session(self):
        """Test connection rejection when session ID is missing"""
        client = socketio.test_client(self.app)
        self.assertFalse(client.is_connected())
    
    def test_connect_invalid_session(self):
        """Test connection rejection for invalid session ID"""
        client = socketio.test_client(self.app, query_string='sessionID=invalid_session')
        self.assertFalse(client.is_connected())
    
    def test_disconnect(self):
        """Test WebSocket disconnection functionality"""
        # Connect first
        client = socketio.test_client(self.app, query_string=f'sessionID={self.user1.session_id}')
        self.assertTrue(client.is_connected())
        
        # Now disconnect
        client.disconnect()
        
        # Check that user is marked as offline
        user = User.query.get(self.user1.user_id)
        self.assertFalse(user.is_online)
        
        # Verify user_sids dictionary is updated
        from app.websocket.websockets import user_sids
        self.assertNotIn(self.user1.user_id, user_sids)
    
    def test_send_message(self):
        """Test sending a message between users"""
        # Connect both users
        client1 = socketio.test_client(self.app, query_string=f'sessionID={self.user1.session_id}')
        client2 = socketio.test_client(self.app, query_string=f'sessionID={self.user2.session_id}')
        
        # Send message from user1 to user2
        message_data = {
            'sessionID': self.user1.session_id,
            'recipient_id': self.user2.user_id,
            'content': 'Hello, User2!',
            'is_group': False,
            'type': 'text'
        }
        client1.emit('send_message', message_data)
        
        # Check that user2 received the message
        received = client2.get_received()
        self.assertTrue(any(event['name'] == 'new_message' for event in received))
        
        # Find the new_message event
        new_message_event = next(event for event in received if event['name'] == 'new_message')
        msg_data = new_message_event['args'][0]
        
        # Verify message data
        self.assertEqual(msg_data['sender_id'], self.user1.user_id)
        self.assertEqual(msg_data['sender_username'], self.user1.username)
        self.assertEqual(msg_data['content'], 'Hello, User2!')
        self.assertEqual(msg_data['type'], 'text')
        self.assertFalse(msg_data['is_group'])
        
        # Check database
        messages = Message.query.filter_by(
            sender_user_id=self.user1.user_id, 
            recipient_user_id=self.user2.user_id
        ).all()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].encrypted_content, 'Hello, User2!')
    
    def test_typing_notification(self):
        """Test typing notification between users"""
        # Connect both users
        client1 = socketio.test_client(self.app, query_string=f'sessionID={self.user1.session_id}')
        client2 = socketio.test_client(self.app, query_string=f'sessionID={self.user2.session_id}')
        
        # Send typing notification from user1 to user2
        typing_data = {
            'action': 'typing',
            'data': {
                'sessionID': self.user1.session_id,
                'recipient_id': self.user2.user_id,
                'char': 'H',
                'is_group': False
            }
        }
        client1.emit('action', typing_data)
        
        # Check that user2 received the typing notification
        received = client2.get_received()
        has_typing = any(event['name'] == 'typing' for event in received)
        self.assertTrue(has_typing, f"No typing event found in {received}")
        
        # Find the typing event
        typing_event = next(event for event in received if event['name'] == 'typing')
        type_data = typing_event['args'][0]
        
        # Verify typing data
        self.assertEqual(type_data['sender_id'], self.user1.user_id)
        self.assertEqual(type_data['sender_username'], self.user1.username)
        self.assertEqual(type_data['char'], 'H')
        self.assertFalse(type_data['is_group'])
    
    def test_add_contact(self):
        """Test adding a contact via WebSocket"""
        # Connect user1
        client1 = socketio.test_client(self.app, query_string=f'sessionID={self.user1.session_id}')
        
        # Connect user3 (not yet a contact of user1)
        client3 = socketio.test_client(self.app, query_string=f'sessionID={self.user3.session_id}')
        
        # User1 adds User3 as contact
        contact_data = {
            'sessionID': self.user1.session_id,
            'contact_username': self.user3.username
        }
        client1.emit('add_contact', contact_data)
        
        # Check that user1 got confirmation
        received1 = client1.get_received()
        has_contact_added = any(event['name'] == 'contact_added' for event in received1)
        self.assertTrue(has_contact_added)
        
        # Check that user3 got a contact request notification
        received3 = client3.get_received()
        has_contact_request = any(event['name'] == 'contact_request' for event in received3)
        self.assertTrue(has_contact_request)
        
        # Check database for the new contact relationship
        contact = UserContact.query.filter_by(
            user_id=self.user1.user_id, 
            contact_id=self.user3.user_id
        ).first()
        self.assertIsNotNone(contact)
        self.assertEqual(contact.status, ContactStatusEnum.NEW)
    
    def test_use_item(self):
        """Test using an item via WebSocket"""
        # Connect both users
        client1 = socketio.test_client(self.app, query_string=f'sessionID={self.user1.session_id}')
        client2 = socketio.test_client(self.app, query_string=f'sessionID={self.user2.session_id}')
        
        # User1 uses an item with User2
        item_data = {
            'action': 'useItem',
            'data': {
                'sessionID': self.user1.session_id,
                'recipient_id': self.user2.user_id,
                'item_id': 'test_item_1',
                'is_group': False
            }
        }
        client1.emit('action', item_data)
        
        # Check that user2 got item used notification
        received = client2.get_received()
        has_item_used = any(event['name'] == 'item_used' for event in received)
        self.assertTrue(has_item_used, f"No item_used event found in {received}")
        
        # Find the item_used event
        item_event = next(event for event in received if event['name'] == 'item_used')
        item_use_data = item_event['args'][0]
        
        # Verify item use data
        self.assertEqual(item_use_data['sender_id'], self.user1.user_id)
        self.assertEqual(item_use_data['sender_username'], self.user1.username)
        self.assertEqual(item_use_data['item_id'], 'test_item_1')
        self.assertFalse(item_use_data['is_group'])
    
    def test_system_message(self):
        """Test sending system messages"""
        # Connect user2
        client2 = socketio.test_client(self.app, query_string=f'sessionID={self.user2.session_id}')
        
        # Connect user1 and send system message to user2
        client1 = socketio.test_client(self.app, query_string=f'sessionID={self.user1.session_id}')
        
        system_msg_data = {
            'action': 'system_message',
            'data': {
                'sessionID': self.user1.session_id,
                'recipient_id': self.user2.user_id,
                'content': 'This is a system notification',
                'is_group': False
            }
        }
        client1.emit('action', system_msg_data)
        
        # Check that user2 received the system message
        received = client2.get_received()
        has_system_msg = any(event['name'] == 'system_message' for event in received)
        self.assertTrue(has_system_msg, f"No system_message event found in {received}")
        
        # Find the system_message event
        sys_event = next(event for event in received if event['name'] == 'system_message')
        sys_data = sys_event['args'][0]
        
        # Verify system message data
        self.assertEqual(sys_data['content'], 'This is a system notification')
        self.assertFalse(sys_data['is_group'])

    def test_send_message_invalid_session(self):
        """Test sending a message with an invalid session ID"""
        client = socketio.test_client(self.app)
        
        message_data = {
            'sessionID': 'invalid_session_id',
            'recipient_id': self.user2.user_id,
            'content': 'This message should not be sent',
            'is_group': False,
            'type': 'text'
        }
        client.emit('send_message', message_data)
        
        # Check database - message should not be stored
        messages = Message.query.filter_by(
            recipient_user_id=self.user2.user_id
        ).all()
        self.assertEqual(len(messages), 0)
    
    def test_send_message_offline_recipient(self):
        """Test sending a message to an offline recipient"""
        # Connect sender
        client1 = socketio.test_client(self.app, query_string=f'sessionID={self.user1.session_id}')
        
        # Make sure user2 is offline (not connected)
        message_data = {
            'sessionID': self.user1.session_id,
            'recipient_id': self.user2.user_id,
            'content': 'Message to offline user',
            'is_group': False,
            'type': 'text'
        }
        client1.emit('send_message', message_data)
        
        # Check database - message should still be stored
        messages = Message.query.filter_by(
            sender_user_id=self.user1.user_id, 
            recipient_user_id=self.user2.user_id
        ).all()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].encrypted_content, 'Message to offline user')
    
    def test_send_message_different_types(self):
        """Test sending different types of messages"""
        # Connect both users
        client1 = socketio.test_client(self.app, query_string=f'sessionID={self.user1.session_id}')
        client2 = socketio.test_client(self.app, query_string=f'sessionID={self.user2.session_id}')
        
        # Send image message
        image_msg = {
            'sessionID': self.user1.session_id,
            'recipient_id': self.user2.user_id,
            'content': 'base64encodedimage',
            'is_group': False,
            'type': 'image'
        }
        client1.emit('send_message', image_msg)
        
        # Check that user2 received the message
        received = client2.get_received()
        new_message_events = [event for event in received if event['name'] == 'new_message']
        self.assertTrue(len(new_message_events) > 0)
        
        # Check the image message
        image_event = new_message_events[0]
        msg_data = image_event['args'][0]
        self.assertEqual(msg_data['type'], 'image')
        self.assertEqual(msg_data['content'], 'base64encodedimage')
        
        # Check database
        messages = Message.query.filter_by(type=MessageTypeEnum.image).all()
        self.assertEqual(len(messages), 1)
    
    def test_action_handler(self):
        """Test the action event handler with different actions"""
        # Connect both users
        client1 = socketio.test_client(self.app, query_string=f'sessionID={self.user1.session_id}')
        client2 = socketio.test_client(self.app, query_string=f'sessionID={self.user2.session_id}')
        
        # Test with action 'sendMessage'
        message_action = {
            'action': 'sendMessage',
            'data': {
                'sessionID': self.user1.session_id,
                'recipient_id': self.user2.user_id,
                'content': 'Message via action handler',
                'is_group': False,
                'type': 'text'
            }
        }
        client1.emit('action', message_action)
        
        # Check that user2 received the message
        received = client2.get_received()
        has_message = any(event['name'] == 'new_message' for event in received)
        self.assertTrue(has_message, f"No new_message event found in {received}")
        
        # Check database
        messages = Message.query.filter_by(
            encrypted_content='Message via action handler'
        ).all()
        self.assertEqual(len(messages), 1)
    
    def test_invalid_action(self):
        """Test sending an invalid action"""
        client1 = socketio.test_client(self.app, query_string=f'sessionID={self.user1.session_id}')
        
        # Send invalid action
        invalid_action = {
            'action': 'nonexistentAction',
            'data': {
                'sessionID': self.user1.session_id,
                'recipient_id': self.user2.user_id
            }
        }
        client1.emit('action', invalid_action)
        
        # Nothing should happen, just make sure it doesn't crash
        # This is a negative test case
    
    def test_multiple_connections(self):
        """Test multiple connections from the same user"""
        # Connect first client
        client1 = socketio.test_client(self.app, query_string=f'sessionID={self.user1.session_id}')
        self.assertTrue(client1.is_connected())
        
        # Connect second client with same session
        client2 = socketio.test_client(self.app, query_string=f'sessionID={self.user1.session_id}')
        self.assertTrue(client2.is_connected())
        
        # Check user_sids dictionary - should have latest SID
        from app.websocket.websockets import user_sids
        self.assertIn(self.user1.user_id, user_sids)
        self.assertEqual(user_sids[self.user1.user_id], client2.sid)
        
        # Disconnect both
        client1.disconnect()
        client2.disconnect()

    def test_missing_data_in_actions(self):
        """Test handling of actions with missing data"""
        client1 = socketio.test_client(self.app, query_string=f'sessionID={self.user1.session_id}')
        
        # Send typing action without required fields
        incomplete_typing = {
            'action': 'typing',
            'data': {
                'sessionID': self.user1.session_id,
                # Missing recipient_id and char
            }
        }
        client1.emit('action', incomplete_typing)
        
        # Nothing should happen, this is to test error handling
        
        # Send message action without content
        incomplete_message = {
            'action': 'sendMessage',
            'data': {
                'sessionID': self.user1.session_id,
                'recipient_id': self.user2.user_id,
                # Missing content
                'is_group': False,
                'type': 'text'
            }
        }
        client1.emit('action', incomplete_message)
        
        # Check that no message was stored
        messages = Message.query.filter_by(
            sender_user_id=self.user1.user_id,
            recipient_user_id=self.user2.user_id
        ).all()
        # Should still be 0 since the message had no content
        self.assertEqual(len(messages), 0)

if __name__ == '__main__':
    unittest.main()
