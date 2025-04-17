from flask import Blueprint, current_app, request, jsonify
from app.extensions import db
from app.models.user import User, UserContact, ContactStatusEnum
from app.services.user_service import UserService
from app.services.message_service import MessageService
from app.services.contact_service import ContactService

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

api_bp = Blueprint('api', __name__)
user_service = UserService()
message_service = MessageService()
contact_service = ContactService()


# User authentication routes
@api_bp.route("/register", methods=['POST'])
def register():
    username = request.args.get('username')
    password = request.args.get('password')
    
    if not username:
        return jsonify({"error": "No username provided for register"}), 400
    if not password:
        return jsonify({"error": "No password provided for register"}), 400
    
    result = user_service.register_user(username, password)
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify({"success": "User registered successfully"})

@api_bp.route("/login", methods=['GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')
    
    if not username:
        return jsonify({"error": "No username provided for login"}), 400
    if not password:
        return jsonify({"error": "No password provided for login"}), 400
    
    result = user_service.login_user(username, password)
    if "error" in result:
        return jsonify(result), 400
    
    access_token = create_access_token(identity=result["user_id"])
    expires_in = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds()

    return jsonify(access_token=access_token, expires_in=expires_in, user_id=result["user_id"])

@api_bp.route("/logout", methods=['POST'])
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    result = user_service.logout_user_by_user_id(user_id)
    if "error" in result:
        return jsonify(result), 400
    return jsonify({"success": "User logged out successfully"})

# Contact management routes
@api_bp.route("/addContact", methods=['POST'])
@jwt_required()
def add_contact():
    user_id = get_jwt_identity()
    contact_id = request.args.get('contactID')
    
    if not contact_id:
        return jsonify({"error": "No contact provided for addContact"}), 400
    
    result = contact_service.add_contact_by_user_id(user_id, contact_id)
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify({"success": "Contact was added successfully"})

@api_bp.route("/changeContact", methods=['POST'])
@jwt_required()
def change_contact():
    user_id = get_jwt_identity()
    contact_id = request.args.get('contactID')
    status = request.args.get('status')
    
    if not contact_id:
        return jsonify({"error": "No contact provided for changeContact"}), 400
    if not status:
        return jsonify({"error": "No status provided for changeContact"}), 400
    
    result = contact_service.change_contact_status_by_user_id(user_id, contact_id, status)
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify({"success": "Contact status changed successfully"})

@api_bp.route("/getContacts", methods=['GET'])
@jwt_required()
def get_contacts():
    user_id = get_jwt_identity()
    result = contact_service.get_user_contacts_by_user_id(user_id)
    if "error" in result:
        return jsonify(result), 400
    return jsonify({"contacts": result})

# Message routes
@api_bp.route("/getContactMessages", methods=['GET'])
@jwt_required()
def get_contact_messages():
    contact_id = request.args.get('contactID')
    user_id = get_jwt_identity()

    if not contact_id:
        return jsonify({"error": "No contactID provided for getContactMessages"}), 400
    
    result, status_code = message_service.get_messages_with_contact(user_id, contact_id)
    return jsonify(result), status_code

@api_bp.route("/saveMessage", methods=["POST"])
@jwt_required()
def save_message():
    user_id = get_jwt_identity()

    # Support both JSON body and query parameters
    data = request.json if request.is_json else request.args

    recipient_id = data.get("recipientID")
    content = data.get("content")
    
    # Handle isGroup that could be either a boolean or a string
    is_group_value = data.get("isGroup", False)
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
