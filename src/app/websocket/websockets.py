from datetime import datetime, timezone, UTC
import uuid
from flask import request
from flask_socketio import SocketIO, emit
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import db, User, Message, MessageTypeEnum
from app.models.user import UserContact, ContactStatusEnum
from app.services.group_service import GroupService

socketio = SocketIO()
group_service = GroupService()
user_sids = {}  # {user_id: socket_id}


def get_user_from_jwt():
    """Helper to get user from JWT token"""
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    return User.query.get(user_id)


###########################
## WEBSOCKET ENDPOINTS
###########################
@socketio.on('connect')
def handle_connect():
    try:
        user = get_user_from_jwt()
        if not user:
            print("Rejecting: Invalid JWT token")
            return False  # Reject connection

        print(f"Accepting connection for user: {user.username}")
        user_sids[user.user_id] = request.sid  # Store the user's socket ID

        user.is_online = True
        db.session.commit()

        # Notify all contacts that the user is online
        emit('user_status', {
            'user_id': user.user_id,
            'username': user.username,
            'status': 'online'
        }, broadcast=True)

        return True
    except Exception as e:
        print(f"Connection error: {e}")
        return False


@socketio.on('disconnect')
def handle_disconnect():
    try:
        user = get_user_from_jwt()
        if user:
            # Update online status
            user.is_online = False
            db.session.commit()
            
            # Remove from tracking
            user_sids.pop(user.user_id, None)

            # Notify all contacts that the user is offline
            emit('user_status', {
                'user_id': user.user_id,
                'username': user.username,
                'status': 'offline'
            }, broadcast=True)
    except Exception as e:
        print(f"Disconnection error: {e}")


# @socketio.on('send_message')
# def handle_message(data):
#     try:
#         user = get_user_from_jwt()
#         recipient_id = data.get('recipient_id')
#         content = data.get('content')
#         msg_type = data.get('type', 'text')
#
#         if not user:
#             return
#
#         if not recipient_id or not content:
#             emit('error', {'message': 'Recipient ID and content are required'})
#             return
#
#         is_group = group_service.does_group_exist(recipient_id)
#
#
#         message = Message(
#             message_id=str(uuid.uuid4()),
#             sender_user_id=user.user_id,
#             recipient_user_id=recipient_id,
#             encrypted_content=content,
#             type=MessageTypeEnum(msg_type),
#             send_at=datetime.utcnow(),
#             is_group=is_group
#         )
#         db.session.add(message)
#         db.session.commit()
#
#         # Send message directly to recipient's socket if they are online
#         if recipient_id in user_sids:
#             emit('new_message', {
#                 'message_id': message.message_id,
#                 'sender_id': user.user_id,
#                 'sender_username': user.username,
#                 'content': content,
#                 'type': msg_type,
#                 'timestamp': message.send_at.isoformat(),
#                 'is_group': is_group
#             }, room=user_sids[recipient_id])
#     except Exception as e:
#         print(f"Message handling error: {e}")
#         emit('error', {'message': 'Failed to send message'})


# New WebSocket Handlers
@socketio.on('action')
def handle_action(data):
    """Handle various client actions based on the action field"""
    try:
        user = get_user_from_jwt()
        if not user:
            return
            
        action = data.get('action')
        action_data = data.get('data', {})
        
        if action == 'typing':
            handle_typing(user, action_data)
        elif action == 'sendMessage':
            handle_send_message(user, action_data)
        elif action == 'useItem':
            handle_use_item(user, action_data)
        elif action == 'system_message':
            handle_system_message(user, action_data)
    except Exception as e:
        print(f"Action handling error: {e}")
        emit('error', {'message': 'Failed to process action'})

def handle_typing(user, data):
    """Handle typing event and notify recipients"""
    recipient_id = data.get('recipient_id')
    character = data.get('char')
    is_group = group_service.does_group_exist(recipient_id)
    
    if not recipient_id or not character:
        return
    
    # Send typing notification directly to recipient's socket if they are online
    if recipient_id in user_sids:
        emit('typing', {
            'sender_id': user.user_id,
            'sender_username': user.username,
            'char': character,
            'timestamp': datetime.utcnow().isoformat(),
            'is_group': is_group
        }, room=user_sids[recipient_id])
    elif is_group:
        # For groups, send to all members
        members = group_service.get_group_members(user.user_id, recipient_id)
        if not isinstance(members, list):
            return
            
        for member in members:
            if member["user_id"] in user_sids and member["user_id"] != user.user_id:
                emit('typing', {
                    'sender_id': user.user_id,
                    'sender_username': user.username,
                    'char': character,
                    'timestamp': datetime.utcnow().isoformat(),
                    'is_group': True,
                    'group_id': recipient_id
                }, room=user_sids[member["user_id"]])

def handle_send_message(user, data):
    """Handle send message action"""
    recipient_id = data.get('recipient_id')
    content = data.get('content')
    is_group = group_service.does_group_exist(recipient_id)
    msg_type = data.get('type', 'text')
    
    if not recipient_id or not content:
        return
    
    message = Message(
        message_id=str(uuid.uuid4()),
        sender_user_id=user.user_id,
        recipient_user_id=recipient_id,
        encrypted_content=content,
        type=MessageTypeEnum(msg_type),
        send_at=datetime.now(UTC),
        is_group=is_group
    )
    db.session.add(message)
    db.session.commit()
    
    # Send notification directly to recipient's socket if they are online
    if recipient_id in user_sids:
        emit('new_message', {
            'message_id': message.message_id,
            'sender_id': user.user_id,
            'sender_username': user.username,
            'content': content,
            'type': msg_type,
            'timestamp': message.send_at.isoformat(),
            'is_group': is_group
        }, room=user_sids[recipient_id])
    elif is_group:
        # For groups, send to all members
        members = group_service.get_group_members(user.user_id, recipient_id)
        if not isinstance(members, list):
            return
            
        for member in members:
            if member["user_id"] in user_sids and member["user_id"] != user.user_id:
                emit('new_message', {
                    'message_id': message.message_id,
                    'sender_id': user.user_id,
                    'sender_username': user.username,
                    'content': content,
                    'type': msg_type,
                    'timestamp': message.send_at.isoformat(),
                    'is_group': True,
                    'group_id': recipient_id
                }, room=user_sids[member["user_id"]])

def handle_use_item(user, data):
    """Handle item usage"""
    recipient_id = data.get('recipient_id')
    item_id = data.get('item_id')
    is_group = group_service.does_group_exist(recipient_id)
    
    if not recipient_id or not item_id:
        return
    
    # Send notification directly to recipient's socket if they are online
    if recipient_id in user_sids:
        emit('item_used', {
            'sender_id': user.user_id,
            'sender_username': user.username,
            'item_id': item_id,
            'timestamp': datetime.utcnow().isoformat(),
            'is_group': is_group
        }, room=user_sids[recipient_id])
    elif is_group:
        # For groups, send to all members
        members = group_service.get_group_members(user.user_id, recipient_id)
        if not isinstance(members, list):
            return
            
        for member in members:
            if member["user_id"] in user_sids and member["user_id"] != user.user_id:
                emit('item_used', {
                    'sender_id': user.user_id,
                    'sender_username': user.username,
                    'item_id': item_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'is_group': True,
                    'group_id': recipient_id
                }, room=user_sids[member["user_id"]])

def handle_system_message(user, data):
    """Handle system messages"""
    recipient_id = data.get('recipient_id')
    content = data.get('content')
    is_group = group_service.does_group_exist(recipient_id)
    
    if not recipient_id or not content:
        return
    
    # Send system message directly to recipient's socket if they are online
    if recipient_id in user_sids:
        emit('system_message', {
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
            'is_group': is_group
        }, room=user_sids[recipient_id])
    elif is_group:
        # For groups, send to all members
        members = group_service.get_group_members(user.user_id, recipient_id)
        if not isinstance(members, list):
            return
            
        for member in members:
            if member["user_id"] in user_sids and member["user_id"] != user.user_id:
                emit('system_message', {
                    'content': content,
                    'timestamp': datetime.utcnow().isoformat(),
                    'is_group': True,
                    'group_id': recipient_id
                }, room=user_sids[member["user_id"]])

# Helper functions to send notifications
def send_typing_notification(user_id, recipient_id, character, is_group=False):
    """Send typing notification to recipient"""
    user = User.query.get(user_id)
    if not user or recipient_id not in user_sids:
        return
        
    socketio.emit('typing', {
        'sender_id': user.user_id,
        'sender_username': user.username,
        'char': character,
        'timestamp': datetime.utcnow().isoformat(),
        'is_group': is_group
    }, room=user_sids[recipient_id])

def send_message_notification(message):
    """Send message notification to recipient"""
    sender = User.query.get(message.sender_user_id)
    if not sender or message.recipient_user_id not in user_sids:
        return
        
    socketio.emit('new_message', {
        'message_id': message.message_id,
        'sender_id': sender.user_id,
        'sender_username': sender.username,
        'content': message.encrypted_content,
        'type': message.type.value,
        'timestamp': message.send_at.isoformat(),
        'is_group': message.is_group
    }, room=user_sids[message.recipient_user_id])
