from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import User, UserContact, ContactStatusEnum
from app.services.user_service import UserService
from app.services.message_service import MessageService
from app.services.contact_service import ContactService

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
    
    return jsonify({"sessionID": result["session_id"]})

@api_bp.route("/logout", methods=['POST'])
def logout():
    session_id = request.args.get('sessionID')
    
    if not session_id:
        return jsonify({"error": "No sessionID provided for logout"}), 400
    
    result = user_service.logout_user(session_id)
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify({"success": "User logged out successfully"})

# Contact management routes
@api_bp.route("/addContact", methods=['POST'])
def add_contact():
    session_id = request.args.get('sessionID')
    contact_id = request.args.get('contactID')
    
    if not session_id:
        return jsonify({"error": "No sessionID provided for addContact"}), 400
    if not contact_id:
        return jsonify({"error": "No contact provided for addContact"}), 400
    
    result = contact_service.add_contact(session_id, contact_id)
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify({"success": "Contact was added successfully"})

@api_bp.route("/changeContact", methods=['POST'])
def change_contact():
    session_id = request.args.get('sessionID')
    contact_id = request.args.get('contactID')
    status = request.args.get('status')
    
    if not session_id:
        return jsonify({"error": "No sessionID provided for changeContact"}), 400
    if not contact_id:
        return jsonify({"error": "No contact provided for changeContact"}), 400
    if not status:
        return jsonify({"error": "No status provided for changeContact"}), 400
    
    result = contact_service.change_contact_status(session_id, contact_id, status)
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify({"success": "Contact status changed successfully"})

@api_bp.route("/getContacts", methods=['GET'])
def get_contacts():
    session_id = request.args.get('sessionID')
    
    if not session_id:
        return jsonify({"error": "No sessionID provided for getContacts"}), 400
    
    result = contact_service.get_user_contacts(session_id)
    if "error" in result:
        return jsonify(result), 400
    
    # Add debug print
    print(f"Returning contacts for session {session_id}: {result}")
    
    return jsonify({"contacts": result})

# Message routes
@api_bp.route("/getContactMessages", methods=['GET'])
def get_contact_messages():
    session_id = request.args.get('sessionID')
    contact_id = request.args.get('contactID')
    
    if not session_id:
        return jsonify({"error": "No sessionID provided for getContactMessages"}), 400
    if not contact_id:
        return jsonify({"error": "No contact provided for getContactMessages"}), 400
    
    result, status_code = message_service.get_messages_with_contact(session_id, contact_id)
    return jsonify(result), status_code

@api_bp.route("/saveMessage", methods=["POST"])
def save_message():
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    session_id = data.get("sessionID")
    recipient_id = data.get("recipientID")
    content = data.get("content")
    
    if not session_id:
        return jsonify({"error": "No sessionID provided for saveMessage"}), 400
    if not recipient_id:
        return jsonify({"error": "No recipientID provided for saveMessage"}), 400
    if not content:
        return jsonify({"error": "No content provided for saveMessage"}), 400
    
    result = message_service.save_message(session_id, recipient_id, content)
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify({"success": "Message saved successfully"})

# Simple test endpoint
@api_bp.route("/")
def default():
    return "UMOC Backend API"

# Debug endpoint
@api_bp.route("/debugContacts", methods=['GET'])
def debug_contacts():
    session_id = request.args.get('sessionID')
    
    if not session_id:
        return jsonify({"error": "No sessionID provided"}), 400
    
    user = User.query.filter_by(session_id=session_id).first()
    if not user:
        return jsonify({"error": "User not found", "session_id": session_id}), 400
    
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
