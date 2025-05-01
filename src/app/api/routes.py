import re
from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
import json
from app.models.user import User, UserContact, ContactStatusEnum
from app.services.user_service import UserService
from app.services.message_service import MessageService
from app.services.contact_service import ContactService
from app.services.group_service import GroupService
from app.extensions import db

api_bp = Blueprint('api', __name__)
user_service = UserService()
message_service = MessageService()
contact_service = ContactService()
group_service = GroupService()


# User authentication routes
@api_bp.route("/register", methods=['POST'])
def register():
    data = request.json if request.is_json else request.args
    username = data.get('username')
    password = data.get('password')
    profile_pic = data.get('profile_pic')

    if not username:
        return jsonify({"error": "Username is required"}), 400
    if not password:
        return jsonify({"error": "Password is required"}), 400

    if not re.match(r'^[a-zA-Z0-9._]+$', username):
        return jsonify({"error": "Username can only contain letters, numbers, dots (.) and underscores (_)"}), 400
    if len(username) < 3 or len(username) > 25:
        return jsonify({"error": "Username must be between 3 and 20 characters long"}), 400

    if len(password) < 4 or len(password) > 100:
        return jsonify({"error": "Password must be between 4 and 100 characters long"}), 400

    result = user_service.register_user(username, password, profile_pic)
    if "error" in result:
        return jsonify({"error": "Username already exists."}), 409  # Conflict for duplicate username

    return jsonify({"success": "User registered successfully"}), 201  # Created


@api_bp.route("/login", methods=['GET'])
def login():
    data = request.json if request.is_json else request.args
    username = data.get('username')
    password = data.get('password')

    if not username:
        return jsonify({"error": "Username is required"}), 400
    if not password:
        return jsonify({"error": "Password is required"}), 400

    result = user_service.login_user(username, password)
    if "error" in result:
        return jsonify({"error": "Invalid credentials"}), 401  # Unauthorized

    access_token = create_access_token(identity=result["user_id"])
    expires_in = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds()

    return jsonify(access_token=access_token, expires_in=expires_in, user_id=result["user_id"])


@api_bp.route("/logout", methods=['POST'])
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    result = user_service.logout_user_by_user_id(user_id)
    if "error" in result:
        return jsonify({"error": "Logout failed"}), 500  # Internal Server Error
    return jsonify({"success": "User logged out successfully"}), 200


# Contact management routes
@api_bp.route("/addContact", methods=['POST'])
@jwt_required()
def add_contact():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    contact_name = data.get('contact_name')

    if not contact_name:
        return jsonify({"error": "Contact name is required"}), 400

    result = contact_service.add_contact_by_name(user_id, contact_name)
    if "error" in result:
        return jsonify(result), 400

    return jsonify({"success": "Contact was added successfully"}), 201


@api_bp.route("/changeContact", methods=['POST'])
@jwt_required()
def change_contact():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    contact_id = data.get('contact_id')
    status = data.get('status')

    if not contact_id:
        return jsonify({"error": "Contact ID is required"}), 400
    if not status:
        return jsonify({"error": "Status is required"}), 400

    result = contact_service.change_contact_status_by_user_id(user_id, contact_id, status)
    if "error" in result:
        return jsonify({"error": "Failed to change contact status"}), 500

    return jsonify({"success": "Contact status changed successfully"}), 200


@api_bp.route("/getChats", methods=['GET'])
@jwt_required()
def get_chats():
    user_id = get_jwt_identity()

    contacts = contact_service.get_user_contacts_by_user_id(user_id)
    if "error" in contacts:
        return jsonify(contacts), 500
    for c in contacts:
        c["is_group"] = False

    groups = group_service.get_groups_by_user_id(user_id)
    if "error" in groups:
        return jsonify(groups), 500
    for g in groups:
        g["is_group"] = True

    return jsonify({"chats": contacts + groups})


# Message routes
@api_bp.route("/getChatMessages", methods=['GET'])
@jwt_required()
def get_chat_messages():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    chat_id = data.get('chat_id')
    page = data.get('page', type=int)
    is_group = data.get('is_group', type=bool, default=False)

    if not chat_id:
        return jsonify({"error": "No chatID provided for getContactMessages"}), 400
    if not user_service.does_user_exist(user_id):
        return jsonify({"error": "User not found"}), 400

    if is_group or group_service.is_id_group(chat_id):
        if not group_service.does_group_exist(chat_id):
            return jsonify({"error": "Group not found"}), 404
        if not group_service.is_user_member(user_id, chat_id):
            return jsonify({"error": "User is not a member of the group"}), 403
        result, status_code = message_service.get_messages_with_groups(user_id, chat_id, page)
    else:
        if not user_service.does_user_exist(chat_id):
            return jsonify({"error": "Contact not found"}), 404
        if not contact_service.is_contact(user_id, chat_id):
            return jsonify({"error": "User is not a contact"}), 403
        result, status_code = message_service.get_messages_with_contact(user_id, chat_id, page)

    return jsonify(result), status_code


@api_bp.route("/saveMessage", methods=["POST"])
@jwt_required()
def save_message():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args

    recipient_id = data.get("recipient_id")
    content = data.get("content")

    # Handle isGroup that could be either a boolean or a string
    is_group_value = data.get("is_group", False)
    if isinstance(is_group_value, bool):
        is_group = is_group_value
    else:
        is_group = str(is_group_value).lower() == "true"

    if not recipient_id:
        return jsonify({"error": "No recipientID provided for saveMessage"}), 400
    if not content:
        return jsonify({"error": "No content provided for saveMessage"}), 400

    result = message_service.save_message(user_id, recipient_id, content, is_group=is_group)
    if "error" in result:
        return jsonify(result), 400

    # Kontakte automatisch hinzufügen (beidseitig)
    for uid, cid in [(user_id, recipient_id), (recipient_id, user_id)]:
        exists = UserContact.query.filter_by(user_id=uid, contact_id=cid).first()
        if not exists:
            db.session.add(UserContact(
                user_id=uid,
                contact_id=cid,
                status=ContactStatusEnum.NEW,
                streak=0,
                continue_streak=True
            ))
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Contact add failed: {str(e)}"}), 500

    return jsonify({"success": "Message saved successfully", "message_id": result["message_id"]})


# Simple test endpoint
@api_bp.route("/")
@jwt_required()
def default():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


# Debug endpoint
@api_bp.route("/debugContacts", methods=['GET'])
@jwt_required()
def debug_contacts():
    user_id = get_jwt_identity()
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 400

    contacts = UserContact.query.filter_by(user_id=user.user_id).all()

    debug_info = {
        "user_id": user.user_id,
        "username": user.username,
        "contact_count": len(contacts),
        "contacts": [
            {
                "contact_id": c.contact_id,
                "status": c.status.value,
                "streak": c.streak
            } for c in contacts
        ]
    }

    return jsonify(debug_info)


# Group Endpoints

@api_bp.route("/createGroup", methods=['POST'])
@jwt_required()
def create_group():
    user_id = get_jwt_identity()
    user = User.query.filter_by(user_id=user_id).first()

    data = request.json if request.is_json else request.args
    group_name = data.get('group_name')
    group_pic = data.get('group_pic')
    group_members = data.get('group_members')
    if isinstance(group_members, str):
        try:
            group_members = json.loads(group_members)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid group_members format"}), 400

    if not user: return jsonify({"error": "User not found"}), 400
    if len(group_name) < 3 or len(group_name) > 25: return jsonify({"error": "Group name must be between 3 and 50 characters long"}), 400
    if not group_name: return jsonify({"error": "Group name is required"}), 400
    if not group_members: return jsonify({"error": "Group members are required"}), 400
    if len(group_members) < 2: return jsonify({"error": "Group must have at least 2 members"}), 400
    if len(group_members) > 50: return jsonify({"error": "Group can have at most 50 members"}), 400

    result = group_service.create_group(
        user_id=user.user_id,
        group_name=group_name,
        group_pic=group_pic,
        group_members=group_members
    )
    if "error" in result:
        return jsonify(result), 400
    return jsonify({"success": "Group created successfully", "group_id": result["group_id"]}), 201


@api_bp.route("/deleteGroup", methods=['POST'])
@jwt_required()
def delete_group():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    group_id = data.get('group_id')

    if not group_id:
        return jsonify({"error": "Group ID is required"}), 400
    if not user_service.does_user_exist(user_id):
        return jsonify({"error": "User not found"}), 400
    if not group_service.does_group_exist(group_id):
        return jsonify({"error": "Group not found"}), 404

    result = group_service.delete_group(user_id, group_id)

    if "error" in result:
        return jsonify(result), 400
    return jsonify({"success": "Group deleted successfully"}), 200


@api_bp.route("/changeGroup", methods=['POST'])
@jwt_required()
def change_group():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    action = data.get("action").lower()
    group_id = data.get("group_id")
    new_value = data.get("new_value")

    if not user_service.does_user_exist(user_id):
        return jsonify({"error": "User not found"}), 400
    if not group_service.does_group_exist(group_id):
        return jsonify({"error": "Group not found"}), 404
    if not group_service.is_user_admin(user_id, group_id):
        return jsonify({"error": "User is not admin of the group"}), 403
    if not action:
        return jsonify({"error": "Action is required. Valid values: name, picture, admin"}), 400
    if not new_value:
        return jsonify({"error": "New value is required"}), 400

    if action == "name":
        group_service.change_group_name(user_id, group_id, new_value)
    elif action == "picture":
        group_service.change_group_picture(user_id, group_id, new_value)
    elif action == "admin":
        # FIX: Use user_service instead of group_service to check if the user exists
        if not user_service.does_user_exist(new_value):
            return jsonify({"error": "New admin user not found"}), 404
        group_service.change_group_admin(user_id, group_id, new_value)
    else:
        return jsonify({"error": "Action is required. Valid values: name, picture, admin"}), 400
    return jsonify({"success": "Group updated successfully"}), 200


@api_bp.route("/addMember", methods=['POST'])
@jwt_required()
def add_member():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    group_id = data.get('group_id')
    new_member_id = data.get('new_member_id')

    if not group_id:
        return jsonify({"error": "Group ID is required"}), 400
    if not new_member_id:
        return jsonify({"error": "New member ID is required"}), 400
    if not user_service.does_user_exist(user_id):
        return jsonify({"error": "User not found"}), 400
    if not user_service.does_user_exist(new_member_id):
        return jsonify({"error": "New member not found"}), 400
    if not group_service.does_group_exist(group_id):
        return jsonify({"error": "Group not found"}), 400
    if not group_service.is_user_admin(user_id, group_id):
        return jsonify({"error": "User is not admin of the group"}), 403
    if group_service.is_user_member(new_member_id, group_id):
        return jsonify({"error": "New member is already in the group"}), 409

    result = group_service.add_member(user_id, group_id, new_member_id)
    if "error" in result:
        return jsonify(result), 400
    return jsonify({"success": "Member added successfully"}), 200


@api_bp.route("/removeMember", methods=['POST'])
@jwt_required()
def remove_member():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    group_id = data.get('group_id')
    member_id = data.get('member_id')
    if not group_id:
        return jsonify({"error": "'group_id' is required"}), 400
    if not member_id:
        return jsonify({"error": "'member_id' is required"}), 400
    if not user_service.does_user_exist(user_id):
        return jsonify({"error": "User not found"}), 400
    if not user_service.does_user_exist(member_id):
        return jsonify({"error": "Member not found"}), 400
    if not group_service.does_group_exist(group_id):
        return jsonify({"error": "Group not found"}), 400
    if not group_service.is_user_admin(user_id, group_id):
        return jsonify({"error": "User is not admin of the group"}), 403
    if not group_service.is_user_member(member_id, group_id):
        return jsonify({"error": "Member is not in the group"}), 409

    result = group_service.remove_member(user_id, group_id, member_id)
    if "error" in result:
        return jsonify(result), 400
    return jsonify({"success": "Member removed successfully"}), 200

@api_bp.route("/getGroupMembers", methods=['GET'])
@jwt_required()
def get_group_members():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    group_id = data.get('group_id')

    if not group_id:
        return jsonify({"error": "Group ID is required"}), 400
    if not user_service.does_user_exist(user_id):
        return jsonify({"error": "User not found"}), 400
    if not group_service.does_group_exist(group_id):
        return jsonify({"error": "Group not found"}), 404

    result = group_service.get_group_members(group_id)
    if "error" in result:
        return jsonify(result), 400
    return jsonify({"members": result}), 200

# Add missing getGroupMessages endpoint
@api_bp.route("/getGroupMessages", methods=['GET'])
@jwt_required()
def get_group_messages():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    group_id = data.get('group_id')
    page = data.get('page', type=int)

    if not group_id:
        return jsonify({"error": "Group ID is required"}), 400
    if not user_service.does_user_exist(user_id):
        return jsonify({"error": "User not found"}), 400
    if not group_service.does_group_exist(group_id):
        return jsonify({"error": "Group not found"}), 404
    if not group_service.is_user_member(user_id, group_id):
        return jsonify({"error": "User is not a member of the group"}), 403

    result, status_code = message_service.get_messages_with_groups(user_id, group_id, page)
    return jsonify(result), status_code

