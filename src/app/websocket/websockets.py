from datetime import datetime, timezone, UTC
import uuid
from flask import request
from flask_socketio import emit, SocketIO
from flask_jwt_extended import decode_token
from app.models import db, User, Message, MessageTypeEnum
from app.models.user import UserContact, ContactStatusEnum
from app.services.group_service import GroupService
from app.services.user_service import UserService
from app.services.item_service import ItemService

socketio = SocketIO(cors_allowed_origins="*")
group_service = GroupService()
user_service = UserService()
items_service = ItemService()

user_sids = {}  # user_id → sid
sid_users = {}  # sid → user_id

def init_websockets(app):
    global socketio
    socketio.init_app(app)


###########################
## WEBSOCKET ENDPOINTS
###########################
@socketio.on('connect')
def handle_connect():
    print("New connection established")
    token = request.args.get('token')
    if not token:
        print("No JWT token provided")
        return False

    try:
        decoded = decode_token(token)
        user_id = decoded["sub"]
        print(f"user who logs in: {user_id}")
        user = User.query.get(user_id)
        if not user:
            return False

        user_sids[user_id] = request.sid
        sid_users[request.sid] = user_id
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
        print(f"JWT decoding error: {e}")
        return False


@socketio.on('disconnect')
def handle_disconnect():
    print("User disconnected")
    try:
        user_id = sid_users.get(request.sid)
        user = User.query.get(user_id)
        if user:
            # Update online status
            user.is_online = False
            db.session.commit()

            del user_sids[user_id]
            del sid_users[request.sid]

            # Notify all contacts that the user is offline
            emit('user_status', {
                'user_id': user.user_id,
                'username': user.username,
                'status': 'offline'
            }, broadcast=True)
    except Exception as e:
        print(f"Disconnection error: {e}")


# New WebSocket Handlers
@socketio.on('send_char')
def send_char(data):
    print("Received action:", data)
    """Handle various client actions based on the action field"""
    try:
        user_id = sid_users.get(request.sid)
        user = User.query.get(user_id)

        recipient_id = data.get('recipient_id')
        character = data.get('char', '')
        is_group = group_service.does_group_exist(recipient_id)
        if not recipient_id:
            return

        active_items = items_service.get_active_items(user_id)
        for item in active_items:
            if item['item_name'] == "timeout":
                return

        # Send typing notification directly to recipient's socket if they are online
        if recipient_id in user_sids:
            emit('receive_char', {
                'sender_id': user.user_id,
                'sender_username': user.username,
                'char': character,
                'is_group': is_group,
                'recipient_id': recipient_id,
            }, room=user_sids[recipient_id])
        elif is_group:
            # For groups, send to all members
            members = group_service.get_group_members(recipient_id)
            if not isinstance(members, list):
                return
            for member in members:
                if member["contact_id"] in user_sids and member["contact_id"] != user.user_id:
                    emit('receive_char', {
                        'sender_id': user.user_id,
                        'sender_username': user.username,
                        'char': character,
                        'is_group': True,
                        'recipient_id': recipient_id
                    }, room=user_sids[member["contact_id"]])

    except Exception as e:
        print(f"Action handling error: {e}")
        emit('error', {'message': 'Failed to process action'})


def send_message(user, recipient_id, content, is_group):
    print("Websocket Sending message:", content)
    """Handle send message action"""
    msg_type = "text"

    if not recipient_id or not content:
        return

    # Send notification directly to recipient's socket if they are online
    if recipient_id in user_sids:
        emit('new_message', {
            'message_id': str(uuid.uuid4()),
            'sender_id': user.user_id,
            'content': content,
            'type': msg_type,
            'timestamp': datetime.now(UTC).isoformat(),
            'is_group': False,
            'recipient_id': recipient_id
        }, room=user_sids[recipient_id], namespace='/')
    elif is_group:
        # For groups, send to all members
        members = group_service.get_group_members(recipient_id)
        if not isinstance(members, list):
            return

        for member in members:
            print("websocket: ", member)
            if member["contact_id"] in user_sids and member["contact_id"] != user.user_id:
                print("websocket emiting: ", content)
                emit('new_message', {
                    'message_id': str(uuid.uuid4()),
                    'sender_id': user.user_id,
                    'content': content,
                    'type': msg_type,
                    'timestamp': datetime.now(UTC).isoformat(),
                    'is_group': True,
                    'recipient_id': recipient_id
                }, room=user_sids[member["contact_id"]], namespace='/')


def chat_change(action, recipient_id, data):
    """Handle chat change actions"""
    print("Websocket Chat change action:", action)
    groupmembers = group_service.get_group_members(recipient_id)
    print("groupmembers: ", groupmembers, type(groupmembers))
    match action:
        case "leave_group":
            print("websocket groupmembers leave: ", groupmembers)
            for member in groupmembers:
                print("websocket member in leave Group: ", member, type(member))
                print(user_sids)
                if member["contact_id"] in user_sids:
                    print("websocket member emit in leave Group: ", member, type(member))
                    emit('chat_change', {
                        'action': action,
                        'group_id': recipient_id,
                        'data': {
                            'user_id': data["user_id"]
                        }
                    }, room=user_sids[member["contact_id"]], namespace='/')


        case "remove_member":
            print("websocket groupmembers remove: ", groupmembers)
            for member in groupmembers:
                print("websocket member in remove Group: ", member, type(member))
                if member["contact_id"] in user_sids and member["contact_id"]:
                    emit('chat_change', {
                        'action': action,
                        'group_id': recipient_id,
                        'data': {
                            'user_id': data["member_id"],
                            'by_user_id': data["by_user_id"]
                        }
                    }, room=user_sids[member["contact_id"]], namespace='/')

            if data["member_id"] in user_sids and data["member_id"]:
                # Notify the user who was removed
                emit('chat_change', {
                    'action': action,
                    'group_id': recipient_id,
                    'data': {
                        'user_id': data["member_id"],
                        'by_user_id': data["by_user_id"]
                    }
                }, room=user_sids[data["member_id"]], namespace='/')


        case "add_member":
            print("websocket groupmembers add: ", groupmembers)
            for member in groupmembers:
                print("websocket member in remove Group: ", member, type(member))
                if member["contact_id"] in user_sids and member["contact_id"]:
                    emit('chat_change', {
                        'action': action,
                        'group_id': recipient_id,
                        'data': {
                            'user_id': data["member_id"],
                            'by_user_id': data["by_user_id"]
                        }
                    }, room=user_sids[member["contact_id"]], namespace='/')


        case "create_group":
            for member in groupmembers:
                print("websocket member: ", member, type(member))
                if member["contact_id"] in user_sids and member["contact_id"]:
                    emit('chat_change', {
                        "action": action,
                        "group_id": recipient_id,
                        "data": {
                            'group_name': data["name"],
                            'group_pic': data["picture_url"],
                            'members': data["members"],
                            'am_admin': data["am_admin"],
                            'created_at': data["created_at"]
                        }
                    }, room=user_sids[member["contact_id"]], namespace='/')


        case "delete_group":
            for member in groupmembers:
                if member["contact_id"] in user_sids and member["contact_id"]:
                    emit('chat_change', {
                        "action": action,
                        "group_id": recipient_id,
                        "data": {}
                    }, room=user_sids[member["contact_id"]], namespace='/')


        case "change_group":
            for member in groupmembers:
                if member["contact_id"] in user_sids and member["contact_id"]:
                    emit('chat_change', {
                        "action": action,
                        "group_id": recipient_id,
                        "data": {
                            'action': data["action"],
                            'new_value': data["new_value"]
                        }
                    }, room=user_sids[member["contact_id"]], namespace='/')


def use_item(from_user_id, to_user_id, item_name, active_until):
    """Handle use item action"""
    print("Websocket Use item action:", item_name, from_user_id, to_user_id)

    try:
        if to_user_id not in user_sids:
            print("User not connected")
            return

        # Emit the item used event to the recipient
        emit('item_used', {
            'item_name': item_name,
            'active_until': active_until.isoformat() if active_until else None,
        }, room=user_sids[to_user_id], namespace='/')
    except Exception as e:
        print("Error emitting item_used event:", e)

def chat_change_alone(user_id):
    print("Chat Change", user_id)
    """Handle chat Change"""
    contacts = UserContact.query.filter_by(user_id=user_id).all()
    print("Contacts for user:", contacts)
    for contact in contacts:

        # Notify the user that the contact has changed
        if contact.contact_id in user_sids:
            print("Emitting chat change for contact:", contact.contact_id)
            emit('chat_change', {
                'user_id': user_id,
            }, room=user_sids[contact.contact_id], namespace='/')

def new_contact(contact_id, user_id):
    print("New contact added", contact_id, user_id)
    """Handle new contact action"""
    if contact_id in user_sids:
        emit('chat_change', {
            'user_id': user_id,
        }, room=user_sids[contact_id], namespace='/')

def updated_message(recipient_id, sender_id):
    """Handle updated message action"""
    print("Websocket Updated message:", recipient_id)
    is_group = group_service.does_group_exist(recipient_id)
    try:
        if is_group:
            members = group_service.get_group_members(recipient_id)
            print("Group members:", members)
            if not isinstance(members, list):
                return
            for member in members:
                print("websocket member: ", member, type(member))
                if member["contact_id"] in user_sids:
                    emit('new_message', {
                        'recipient_id': recipient_id,
                        'is_group': is_group,
                        'sender_id': sender_id,
                    }, room=user_sids[member["contact_id"]], namespace='/')
        else:
            print("Single recipient:", recipient_id)
            if recipient_id in user_sids:
                print("Emitting updated_message to recipient:", recipient_id)
            else:
                print("Recipient not connected:", recipient_id)
            emit('new_message', {
                'recipient_id': recipient_id,
                'is_group': is_group,
                'sender_id': sender_id,
            }, room=user_sids[recipient_id], namespace='/')
    except Exception as e:
        print("Error emitting updated_message event:", e)