from datetime import datetime
from sqlalchemy import or_
from app.extensions import db
from app.models.message import Message, MessageTypeEnum
from app.models.user import User, UserContact
from app.services.user_service import UserService

class MessageService:
    def __init__(self):
        self.user_service = UserService()
    
    def save_message(self, session_id, recipient_id, content, is_group=False, message_type=MessageTypeEnum.TEXT):
        user = self.user_service.get_user_by_session(session_id)
        if not user:
            return {"error": "Invalid session ID"}
        
        # Validate recipient exists
        recipient = self.user_service.get_user_by_id(recipient_id)
        if not recipient:
            return {"error": "Recipient not found"}
        
        # Check if users are contacts (should be added for production)
        # contact = UserContact.query.filter_by(user_id=user.user_id, contact_id=recipient_id).first()
        # if not contact:
        #     return {"error": "Recipient is not in your contacts"}
        
        message = Message(
            sender_user_id=user.user_id,
            recipient_user_id=recipient_id,
            encrypted_content=content,
            type=message_type,
            send_at=datetime.utcnow(),
            is_group=is_group
        )
        
        db.session.add(message)
        try:
            db.session.commit()
            return {"success": True, "message_id": message.message_id}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}
    
    def get_messages_with_contact(self, session_id, contact_id):
        user = self.user_service.get_user_by_session(session_id)
        if not user:
            return {"error": "Invalid session ID"}
        
        # Validate contact exists
        contact = self.user_service.get_user_by_id(contact_id)
        if not contact:
            return {"error": "Contact not found"}
        
        # Check if users are contacts
        user_contact = UserContact.query.filter_by(user_id=user.user_id, contact_id=contact_id).first()
        if not user_contact:
            return {"error": "Contact relationship not found"}
        
        # Get messages between the two users
        messages = Message.query.filter(
            or_(
                (Message.sender_user_id == user.user_id) & (Message.recipient_user_id == contact_id),
                (Message.sender_user_id == contact_id) & (Message.recipient_user_id == user.user_id)
            )
        ).order_by(Message.send_at.desc()).all()
        
        return [
            {
                "content": message.encrypted_content, 
                "sender_user_id": message.sender_user_id, 
                "send_at": message.send_at
            } 
            for message in messages
        ]
