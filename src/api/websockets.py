from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import uuid
from src.api.database.models import db, User, UserContact, Message, Group, GroupMember, ContactStatusEnum, MessageTypeEnum

from src.api.database.models import User

socketio = SocketIO()
active_sessions = {}  # {session_id: user_id}
user_sids = {}  # {user_id: socket_id}


def get_user_from_session(session_id):
    """Helper to get user from session ID"""
    if session_id not in active_sessions:
        return None
    return User.query.filter_by(user_id=active_sessions[session_id]).first()


###########################
## WEBSOCKET ENDPOINTS
###########################
@socketio.on('connect')
def handle_connect():
    session_id = request.args.get('session_id')
    if not session_id:
        return False

    user = get_user_from_session(session_id)
    if not user:
        return False

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


@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.args.get('session_id')
    if not session_id or session_id not in active_sessions:
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
    session_id = data.get('session_id')
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
    session_id = data.get('session_id')
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