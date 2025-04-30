from datetime import datetime
import uuid
from flask import request
from flask_socketio import SocketIO, emit, join_room
from app.models import db, User, UserContact, Message, ContactStatusEnum, MessageTypeEnum

socketio = SocketIO()
user_sids = {}  # {user_id: socket_id}


def get_user_from_session(session_id):
    """Helper to get user from session ID"""
    # if session_id not in active_sessions:
    #     return None
    return User.query.filter_by(session_id=session_id).first()


###########################
## WEBSOCKET ENDPOINTS
###########################
@socketio.on('connect')
def handle_connect():
    session_id = request.args.get('sessionID')
    print(f"Connection attempt with session ID: {session_id}")  # Debug log

    if not session_id:
        print("Rejecting: Missing session ID")  # Debug log
        return False  # Reject connection

    # if session_id not in active_sessions:
    #     print(f"Rejecting: Invalid session ID: {session_id}")  # Debug log
    #     return False  # Reject connection

    user = get_user_from_session(session_id)
    if not user:
        print(f"Rejecting: No user found for session ID: {session_id}")  # Debug log
        return False  # Reject connection

    print(f"Accepting connection for user: {user.username}")  # Debug log
    user_sids[user.user_id] = request.sid

    user.is_online = True
    db.session.commit()

    # Join rooms for all contacts and groups
    for contact in user.contacts:
        if contact.status == ContactStatusEnum.FRIEND:
            join_room(f"dm_{min(user.user_id, contact.contact_id)}_{max(user.user_id, contact.contact_id)}")

    for membership in user.group_memberships:
        join_room(f"group_{membership.group_id}")

    # Notify contacts that user is online
    for contact in user.contacts:
        if contact.contact_id in user_sids:
            emit('user_status', {
                'user_id': user.user_id,
                'username': user.username,
                'status': 'online'
            }, room=user_sids[contact.contact_id])

    return True


@socketio.on('disconnect', namespace='/')
def handle_disconnect():
    session_id = request.args.get('sessionID')
    if not session_id:
        return

    user = get_user_from_session(session_id)
    if user:
        # Update online status
        user.is_online = False
        db.session.commit()

        # Remove from tracking
        user_sids.pop(user.user_id, None)

        # Notify contacts user is offline
        for contact in user.contacts:
            if contact.contact_id in user_sids:
                emit('user_status', {
                    'user_id': user.user_id,
                    'username': user.username,
                    'status': 'offline'
                }, room=user_sids[contact.contact_id])


@socketio.on('send_message')
def handle_message(data):
    session_id = data.get('sessionID')
    recipient_id = data.get('recipient_id')
    content = data.get('content')
    is_group = data.get('is_group', False)
    msg_type = data.get('type', 'text')

    sender = get_user_from_session(session_id)
    if not sender:
        return

    message = Message(
        message_id=str(uuid.uuid4()),
        sender_user_id=sender.user_id,
        recipient_user_id=recipient_id,
        encrypted_content=content,
        type=MessageTypeEnum(msg_type),
        send_at=datetime.utcnow(),
        is_group=is_group
    )
    db.session.add(message)
    db.session.commit()

    if is_group:
        room_id = f"group_{recipient_id}"
    else:
        room_id = f"dm_{min(sender.user_id, recipient_id)}_{max(sender.user_id, recipient_id)}"

    emit('new_message', {
        'message_id': message.message_id,
        'sender_id': sender.user_id,
        'sender_username': sender.username,
        'content': content,
        'type': msg_type,
        'timestamp': message.send_at.isoformat(),
        'is_group': is_group
    }, room=room_id)


@socketio.on('add_contact')
def handle_add_contact(data):
    session_id = data.get('sessionID')
    contact_username = data.get('contact_username')

    user = get_user_from_session(session_id)
    if not user:
        return

    contact = User.query.filter_by(username=contact_username).first()
    if not contact:
        emit('error', {'message': 'User not found'}, room=request.sid)
        return

    # Create contact relationship
    new_contact = UserContact(
        user_id=user.user_id,
        contact_id=contact.user_id,
        status=ContactStatusEnum.NEW
    )
    db.session.add(new_contact)
    db.session.commit()

    # Notify both users
    contact_data = {
        'user_id': contact.user_id,
        'username': contact.username,
        'status': ContactStatusEnum.NEW.value
    }
    emit('contact_added', contact_data, room=request.sid)

    if contact.user_id in user_sids:
        emit('contact_request', {
            'user_id': user.user_id,
            'username': user.username
        }, room=user_sids[contact.user_id])

# New WebSocket Handlers
@socketio.on('action')
def handle_action(data):
    """Handle various client actions based on the action field"""
    action = data.get('action')
    action_data = data.get('data', {})
    session_id = action_data.get('sessionID')

    sender = get_user_from_session(session_id)
    if not sender:
        return
    
    if action == 'typing':
        handle_typing(sender, action_data)
    elif action == 'sendMessage':
        handle_send_message(sender, action_data)
    elif action == 'useItem':
        handle_use_item(sender, action_data)
    elif action == 'system_message':
        handle_system_message(sender, action_data)

def handle_typing(sender, data):
    """Handle typing event and notify recipients"""
    recipient_id = data.get('recipient_id')
    character = data.get('char')
    is_group = data.get('is_group', False)
    
    if not recipient_id or not character:
        return
    
    if is_group:
        room_id = f"group_{recipient_id}"
    else:
        room_id = f"dm_{min(sender.user_id, recipient_id)}_{max(sender.user_id, recipient_id)}"
    
    emit('typing', {
        'sender_id': sender.user_id,
        'sender_username': sender.username,
        'char': character,
        'timestamp': datetime.utcnow().isoformat(),
        'is_group': is_group
    }, room=room_id)

def handle_send_message(sender, data):
    """Handle send message action"""
    recipient_id = data.get('recipient_id')
    content = data.get('content')
    is_group = data.get('is_group', False)
    msg_type = data.get('type', 'text')
    
    if not recipient_id or not content:
        return
    
    message = Message(
        message_id=str(uuid.uuid4()),
        sender_user_id=sender.user_id,
        recipient_user_id=recipient_id,
        encrypted_content=content,
        type=MessageTypeEnum(msg_type),
        send_at=datetime.utcnow(),
        is_group=is_group
    )
    db.session.add(message)
    db.session.commit()
    
    if is_group:
        room_id = f"group_{recipient_id}"
    else:
        room_id = f"dm_{min(sender.user_id, recipient_id)}_{max(sender.user_id, recipient_id)}"
    
    emit('new_message', {
        'message_id': message.message_id,
        'sender_id': sender.user_id,
        'sender_username': sender.username,
        'content': content,
        'type': msg_type,
        'timestamp': message.send_at.isoformat(),
        'is_group': is_group
    }, room=room_id)

def handle_use_item(sender, data):
    """Handle item usage"""
    recipient_id = data.get('recipient_id')
    item_id = data.get('item_id')
    is_group = data.get('is_group', False)
    
    if not recipient_id or not item_id:
        return
    
    # Here you'd add logic to process the item usage
    # For now, we'll just notify the recipients
    
    if is_group:
        room_id = f"group_{recipient_id}"
    else:
        room_id = f"dm_{min(sender.user_id, recipient_id)}_{max(sender.user_id, recipient_id)}"
    
    emit('item_used', {
        'sender_id': sender.user_id,
        'sender_username': sender.username,
        'item_id': item_id,
        'timestamp': datetime.utcnow().isoformat(),
        'is_group': is_group
    }, room=room_id)

def handle_system_message(sender, data):
    """Handle system messages"""
    recipient_id = data.get('recipient_id')
    content = data.get('content')
    is_group = data.get('is_group', False)
    
    if not recipient_id or not content:
        return
    
    if is_group:
        room_id = f"group_{recipient_id}"
    else:
        if recipient_id in user_sids:
            room_id = user_sids[recipient_id]
        else:
            return  # Recipient not online
    
    emit('system_message', {
        'content': content,
        'timestamp': datetime.utcnow().isoformat(),
        'is_group': is_group
    }, room=room_id)

# Helper functions to send notifications
def send_typing_notification(user_id, recipient_id, character, is_group=False):
    """Send typing notification to recipient"""
    user = User.query.get(user_id)
    if not user:
        return
        
    if is_group:
        room_id = f"group_{recipient_id}"
    else:
        room_id = f"dm_{min(user_id, recipient_id)}_{max(user_id, recipient_id)}"
    
    socketio.emit('typing', {
        'sender_id': user.user_id,
        'sender_username': user.username,
        'char': character,
        'timestamp': datetime.utcnow().isoformat(),
        'is_group': is_group
    }, room=room_id)

def send_message_notification(message):
    """Send message notification to recipient"""
    sender = User.query.get(message.sender_user_id)
    if not sender:
        return
        
    if message.is_group:
        room_id = f"group_{message.recipient_user_id}"
    else:
        room_id = f"dm_{min(message.sender_user_id, message.recipient_user_id)}_{max(message.sender_user_id, message.recipient_user_id)}"
    
    socketio.emit('new_message', {
        'message_id': message.message_id,
        'sender_id': sender.user_id,
        'sender_username': sender.username,
        'content': message.encrypted_content,
        'type': message.type.value,
        'timestamp': message.send_at.isoformat(),
        'is_group': message.is_group
    }, room=room_id)
