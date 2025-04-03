from flask import request
from flask_socketio import emit, join_room, leave_room
from datetime import datetime
import uuid

# Use absolute imports for app modules
from app.extensions import socketio, db
from app.models.user import User, UserContact, ContactStatusEnum
from app.models.message import Message, MessageTypeEnum
from app.services.user_service import UserService
from app.services.message_service import MessageService

# Track connected users
user_sids = {}  # {user_id: socket_id}
user_service = UserService()
message_service = MessageService()

def get_user_from_session(session_id):
    """Helper to get user from session ID"""
    return User.query.filter_by(session_id=session_id).first()

@socketio.on('connect')
def handle_connect():
    session_id = request.args.get('sessionID')
    print(f"Connection attempt with session ID: {session_id}")

    if not session_id:
        print("Rejecting: Missing session ID")
        return False

    user = get_user_from_session(session_id)
    if not user:
        print(f"Rejecting: No user found for session ID: {session_id}")
        return False

    print(f"Accepting connection for user: {user.username}")
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

@socketio.on('disconnect')
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

    # Create and save message
    result = message_service.save_message(
        session_id, 
        recipient_id, 
        content, 
        is_group, 
        MessageTypeEnum(msg_type)
    )
    
    if "error" in result:
        emit('error', {'message': result["error"]}, room=request.sid)
        return
    
    message_id = result["message_id"]

    # Determine room ID for the message
    if is_group:
        room_id = f"group_{recipient_id}"
    else:
        room_id = f"dm_{min(sender.user_id, recipient_id)}_{max(sender.user_id, recipient_id)}"

    # Broadcast message to the room
    emit('new_message', {
        'message_id': message_id,
        'sender_id': sender.user_id,
        'sender_username': sender.username,
        'content': content,
        'type': msg_type,
        'timestamp': datetime.utcnow().isoformat(),
        'is_group': is_group
    }, room=room_id)

@socketio.on('add_contact')
def handle_add_contact(data):
    session_id = data.get('sessionID')
    contact_username = data.get('contact_username')

    user = get_user_from_session(session_id)
    if not user:
        emit('error', {'message': 'Invalid session'}, room=request.sid)
        return

    contact = User.query.filter_by(username=contact_username).first()
    if not contact:
        emit('error', {'message': 'User not found'}, room=request.sid)
        return

    # Check if contact already exists
    existing = UserContact.query.filter_by(
        user_id=user.user_id, 
        contact_id=contact.user_id
    ).first()
    
    if existing:
        emit('error', {'message': 'Contact already added'}, room=request.sid)
        return

    # Create contact relationship
    new_contact = UserContact(
        user_id=user.user_id,
        contact_id=contact.user_id,
        status=ContactStatusEnum.NEW,
        streak=0,
        continue_streak=True
    )
    db.session.add(new_contact)
    db.session.commit()

    # Notify the requester
    contact_data = {
        'user_id': contact.user_id,
        'username': contact.username,
        'status': ContactStatusEnum.NEW.value
    }
    emit('contact_added', contact_data, room=request.sid)

    # Notify the contact if they're online
    if contact.user_id in user_sids:
        emit('contact_request', {
            'user_id': user.user_id,
            'username': user.username
        }, room=user_sids[contact.user_id])
