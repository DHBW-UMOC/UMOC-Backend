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
from app.services.item_service import ItemService
from app import db

from app.websocket import websockets

api_bp = Blueprint('api', __name__)
user_service = UserService()
message_service = MessageService()
contact_service = ContactService()
group_service = GroupService()
items_service = ItemService()


#############################
## HELPER FUNCTION
#############################

def add_last_message_to_chats(user_id, chats: list) -> list:
    """
    Adds the last message timestamp to each chat in the list of chats.
    Or if group when joined. Else 2001-09-11T12:46:00Z.
    """
    for chat in chats:
        last_message_date = message_service.get_last_message_date_for_contact(user_id, chat["contact_id"])

        if last_message_date:
            chat["last_message_timestamp"] = last_message_date
        else:
            if group_service.is_id_group(chat["contact_id"]):
                chat["last_message_timestamp"] = chat.get("joined_at", "2001-09-11T12:46:00Z")
            else:
                chat["last_message_timestamp"] = "2001-09-11T12:46:00Z"
    return chats



#############################
## ENDPOINTS
#############################

# User authentication routes
@api_bp.route("/register", methods=['POST'])
def register():
    data = request.json if request.is_json else request.args
    username = data.get('username')
    password = data.get('password')
    profile_pic = data.get('profile_pic')

    if not username:
        return jsonify({"error": "'username' is required"}), 400
    if not password:
        return jsonify({"error": "'password' is required"}), 400

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
        return jsonify({"error": "'username' is required"}), 400
    if not password:
        return jsonify({"error": "'password' is required"}), 400

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
        return jsonify({"error": "'contact_name' is required"}), 400

    result = contact_service.add_contact_by_name(user_id, contact_name)
    websockets.chat_change_alone(user_id)
    if "error" in result:
        return jsonify(result), 400

    return jsonify({"success": "Contact was added successfully"}), 201


@api_bp.route("/changeContact", methods=['POST'])
@jwt_required()
def change_contact():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    contact_id = data.get('contact_id')
    status = data.get('status').lower()

    if not contact_id:
        return jsonify({"error": "'contact_id' is required"}), 400
    if not status:
        return jsonify({"error": "'status' is required"}), 400

    # Validate status is a valid enum value
    valid_statuses = [e.value for e in ContactStatusEnum]
    if status not in valid_statuses:
        return jsonify({"error": f"Invalid status. Valid options: {', '.join(valid_statuses)}"}), 400

    # Prevent manual setting of system-controlled statuses
    if status in ["new", "last_words", "timeout"]:
        return jsonify({"error": f"Status '{status}' cannot be set manually. It is controlled by the system."}), 400

    # Only allow manual setting of friend, block, and timeout
    allowed_manual_statuses = ["friend", "block", "unblock", "unfriend"]
    if status not in allowed_manual_statuses:
        return jsonify({"error": f"Status '{status}' cannot be set manually. Allowed statuses: {', '.join(allowed_manual_statuses)}"}), 400

    result = contact_service.change_contact_status_by_user_id(user_id, contact_id, status)
    websockets.chat_change_alone(user_id)
    if "error" in result:
        return jsonify(result), 500

    return jsonify(result), 200


@api_bp.route("/changeProfile", methods=['POST'])
@jwt_required()
def change_profile():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    new_value = data.get('new_value')
    action = data.get('action')

    if not action:
        return jsonify({"error": "'action' is required"}), 400
    if action not in ["picture", "name", "password"]:
        return jsonify({"error": "'action' must be either 'picture', 'name' or 'password'"}), 400
    if action == "picture":
        if not new_value:
            return jsonify({"error": "'new_value' is required"}), 400
        result = user_service.change_profile_picture(user_id, new_value)
    elif action == "name":
        new_value = data.get('new_value')
        if not new_value:
            return jsonify({"error": "'new_value' is required"}), 400
        result = user_service.change_username(user_id, new_value)
    elif action == "password":
        new_value = data.get('new_value')
        if not new_value:
            return jsonify({"error": "'new_value' is required"}), 400
        old_password = data.get('old_password')
        if not old_password:
            return jsonify({"error": "'old_password' is required"}), 400
        result = user_service.change_password(user_id, old_password, new_value)
    websockets.chat_change_alone(user_id)

    # Check if there was an error in the service call
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify({"success": f"Profile {action} updated successfully"}), 200


@api_bp.route("/getChats", methods=['GET'])
@jwt_required()
def get_chats():
    user_id = get_jwt_identity()

    contacts = contact_service.get_user_contacts_by_user_id(user_id)
    if "error" in contacts:
        return jsonify(contacts), 500

    groups = group_service.get_groups_by_user_id(user_id)
    if "error" in groups:
        return jsonify(groups), 500

    return jsonify({"chats": add_last_message_to_chats(user_id, contacts + groups)})


@api_bp.route("/getAllUsers", methods=['GET'])
@jwt_required()
def get_all_users():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    searchBy = data.get('searchBy')

    if not searchBy:
        return jsonify({"error": "No search Filter provided for getAllUsers"}), 400
    if not user_service.does_user_exist(user_id):
        return jsonify({"error": "User not found"}), 400
    
    result = user_service.get_all_users_by_word(searchBy)
    if "error" in result:
        return jsonify(result), 400
    return jsonify({"users": result}), 200


# Message routes
@api_bp.route("/getChatMessages", methods=['GET'])
@jwt_required()
def get_chat_messages():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    chat_id = data.get('chat_id')
    page = data.get('page', type=int)

    if not chat_id:
        return jsonify({"error": "'chat_id' is required"}), 400
    if not user_service.does_user_exist(user_id):
        return jsonify({"error": "User not found"}), 400

    if group_service.is_id_group(chat_id):
        if not group_service.does_group_exist(chat_id):
            return jsonify({"error": "Group not found"}), 404
        if not group_service.is_user_member(user_id, chat_id):
            return jsonify({"error": "User is not a member of the group"}), 403
        result, status_code = message_service.get_messages_with_groups(user_id, chat_id, page)
    else:
        if not user_service.does_user_exist(chat_id):
            return jsonify({"error": "Contact not found"}), 404
        result, status_code = message_service.get_messages_with_contact(user_id, chat_id, page)

    return jsonify(result), status_code


@api_bp.route("/getOwnProfile", methods=['GET'])
@jwt_required()
def get_own_profile():
    user_id = get_jwt_identity()

    if not user_service.does_user_exist(user_id):
        return jsonify({"error": "User not found"}), 400

    user = user_service.get_user_by_id(user_id)
    return jsonify({
        "user_id": user.user_id,
        "username": user.username,
        "profile_picture": user.profile_picture,
        "points": user_service.get_user_points(user_id),
    })


@api_bp.route("/saveMessage", methods=["POST"])
@jwt_required()
def save_message():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    user = User.query.filter_by(user_id=user_id).first()
    recipient_id = data.get("recipient_id")
    content = data.get("content")
    is_group = group_service.does_group_exist(recipient_id)
    active_items = items_service.get_active_items(user_id)

    if active_items:  # Check if the list is not empty before iterating
        for item in active_items:
            if item['item_name'] == "timeout":
                return jsonify({"error": "You are currently in timeout and cannot send messages", "until": item['active_until']}), 403


    if not recipient_id:
        return jsonify({"error": "'recipient_id' is required"}), 400
    if not content:
        return jsonify({"error": "'content' is required"}), 400

    try:
        # Check if the sender (current user) is blocked by the recipient
        recipient_info = UserContact.query.filter_by(user_id=user_id, contact_id=recipient_id).first()
    except:
        return jsonify({"error": "recipient information could not be gathered"}), 400

    # Check if sender is blocked by recipient
    if recipient_info and (recipient_info.status == ContactStatusEnum.BLOCK or recipient_info.status == ContactStatusEnum.FBLOCKED):
        return jsonify({"error": "Unable to send message because of user rules"}), 403    # Save the message first
    result = message_service.save_message(user_id, recipient_id, content, is_group=is_group)
    
    if "error" in result:
        return jsonify(result), 400

    # Update streak after successful message send (only for direct messages, not groups)
    if not is_group:
        contact_service.update_streak(user_id, recipient_id)
    
    # Handle LASTWORDS status after successful message save
    is_last_words = recipient_info and recipient_info.status == ContactStatusEnum.LASTWORDS
    if is_last_words:
        recipient_info.status = ContactStatusEnum.FBLOCKED
        db.session.commit()    # Send websocket message (unless it was last words)
    if not is_last_words:
        websockets.send_message(user, recipient_id, content, is_group=is_group)

    # Kontakte automatisch hinzufügen (beidseitig) - only for direct messages, not groups
    if not is_group:
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
                websockets.new_contact(cid, uid)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Contact add failed: {str(e)}"}), 500

    # Return appropriate response based on status
    if is_last_words:
        return jsonify({"success": "Your last message has been send you are now blocked"}), 200
    else:
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

    if not user: 
        return jsonify({"error": "User not found"}), 400

    # Let group_service handle adding the creator as admin
    result = group_service.create_group(
        user_id=user.user_id,
        group_name="New Group",  # Static name as intended
        group_pic="https://www.svgrepo.com/show/4552/user-groups.svg",  # Empty default picture
        group_members=[]  # Don't add members here, let service handle it
    )
    
    if "error" in result:
        return jsonify(result), 400
    
    # Create complete group structure like in get_groups_by_user_id
    group_data = {
        **result["group"].to_dict(),
        "am_admin": result["am_admin"],
        "members": result["members"]
    }
    
    # Pass the result directly to websocket (let it handle serialization)
    websockets.chat_change("create_group", result["group"].group_id, group_data)
    return jsonify({"group": group_data}), 201


@api_bp.route("/deleteGroup", methods=['POST'])
@jwt_required()
def delete_group():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    group_id = data.get('group_id')

    if not group_id:
        return jsonify({"error": "'group_id' is required"}), 400
    if not user_service.does_user_exist(user_id):
        return jsonify({"error": "User not found"}), 400
    if not group_service.does_group_exist(group_id):
        return jsonify({"error": "Group not found"}), 404

    websockets.chat_change("delete_group", group_id, {})
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

    if not group_id:
        return jsonify({"error": "'group_id' is required"}), 400
    if not new_value:
        return jsonify({"error": "'new_value' is required"}), 400
    if not user_service.does_user_exist(user_id):
        return jsonify({"error": "User not found"}), 400
    if not group_service.does_group_exist(group_id):
        return jsonify({"error": "Group not found"}), 404
    if not group_service.is_user_admin(user_id, group_id):
        return jsonify({"error": "User is not admin of the group"}), 403
    if not action:
        return jsonify({"error": "'action' is required. Valid values: name, picture, admin"}), 400
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
        group_service.change_group_admin(user_id, group_id, new_value, "add")
    elif action == "deadmin":
        # FIX: Use user_service instead of group_service to check if the user exists
        if not user_service.does_user_exist(new_value):
            return jsonify({"error": "User not found"}), 404
        group_service.change_group_admin(user_id, group_id, new_value, "remove")
    else:
        return jsonify({"error": "Action is required. Valid values: name, picture, admin"}), 400

    websockets.chat_change("change_group", group_id, {"action": action, "new_value": new_value})
    return jsonify({"success": "Group updated successfully"}), 200


@api_bp.route("/addMember", methods=['POST'])
@jwt_required()
def add_member():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    group_id = data.get('group_id')
    new_member_id = data.get('new_member_id')

    if not group_id:
        return jsonify({"error": "'group_id' is required"}), 400
    if not new_member_id:
        return jsonify({"error": "'new_member_id' is required"}), 400
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

    websockets.chat_change("add_member", group_id, {"member_id": new_member_id, "by_user_id": user_id})
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

    websockets.chat_change("remove_member", group_id, {"member_id": member_id, "by_user_id": user_id})
    return jsonify({"success": "Member removed successfully"}), 200


@api_bp.route("/leaveGroup", methods=['GET', 'POST'])
@jwt_required()
def leave_group():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    group_id = data.get('group_id')

    if not group_id:
        return jsonify({"error": "'group_id' is required"}), 400
    if not user_service.does_user_exist(user_id):
        return jsonify({"error": "User not found"}), 400
    if not group_service.does_group_exist(group_id):
        return jsonify({"error": "Group not found"}), 404
    if not group_service.is_user_member(user_id, group_id):
        return jsonify({"error": "User is not a member of the group"}), 403

    result = group_service.leave_group(user_id, group_id)
    if "error" in result:
        return jsonify(result), 400

    websockets.chat_change("leave_group", group_id, {"user_id": user_id})
    return jsonify({"success": "User left the group successfully"}), 200


#######################
### Endpoints for Items
#######################

@api_bp.route("/getItemList", methods=['GET'])
def get_item_list():
    items = items_service.get_item_list()
    return jsonify({"items": items}), 200


@api_bp.route("/getInventory", methods=['GET'])
@jwt_required()
def get_inventory():
    user_id = get_jwt_identity()
    if not user_service.does_user_exist(user_id):
        return jsonify({"error": "User not found"}), 400

    inventory = items_service.get_inventory(user_id)
    return jsonify({"inventory": inventory}), 200

@api_bp.route("/getActiveItems", methods=['GET'])
@jwt_required()
def get_active_items():
    user_id = get_jwt_identity()
    if not user_service.does_user_exist(user_id):
        return jsonify({"error": "User not found"}), 400

    active_items = items_service.get_active_items(user_id)
    return jsonify({"active_items": active_items}), 200


@api_bp.route("/useItem", methods=['POST'])
@jwt_required()
def use_item():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    item_name = data.get('item_name')
    to_user_id = data.get('to_user_id')

    if not item_name:
        return jsonify({"error": "'item_name' is required"}), 400
    if not user_service.does_user_exist(user_id):
        return jsonify({"error": "User not found"}), 400

    result, date = items_service.use_item(item_name, user_id, to_user_id)
    if "error" in result:
        return jsonify(result), 400

    websockets.use_item(user_id, to_user_id, item_name, date)

    return jsonify({"success": "Item used successfully"}), 200


@api_bp.route("/buyItem", methods=['POST'])
@jwt_required()
def buy_item():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    item_name = data.get('item_name')

    if not item_name:
        return jsonify({"error": "'item_name' is required"}), 400
    if not user_service.does_user_exist(user_id):
        return jsonify({"error": "User not found"}), 400

    result = items_service.buy_item(item_name, user_id)
    if "error" in result:
        return jsonify(result), 400

    return jsonify({"success": "Item bought successfully"}), 200

@api_bp.route("/deleteMessage", methods=['POST'])
@jwt_required()
def delete_message():
    user_id = get_jwt_identity()
    data = request.json if request.is_json else request.args
    message_id = data.get('message_id')

    if not message_id:
        return jsonify({"error": "'message_id' is required"}), 400
    if not user_service.does_user_exist(user_id):
        return jsonify({"error": "User not found"}), 400

    result = message_service.delete_message(user_id, message_id)
    if "error" in result:
        return jsonify(result), 400

    recipient_id = message_service.get_recipient_id_by_message_id(message_id)
    websockets.updated_message(recipient_id, user_id)
    return jsonify({"success": "Message deleted successfully"}), 200
