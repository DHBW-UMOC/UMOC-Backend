from app.extensions import db
from app.models.user import User, UserContact, ContactStatusEnum
from app.services.user_service import UserService
from sqlalchemy import func

class ContactService:
    def __init__(self):
        self.user_service = UserService()
    
    def add_contact(self, session_id, contact_id):
        user = self.user_service.get_user_by_session(session_id)
        if not user:
            return {"error": "Invalid session ID"}
        
        contact = self.user_service.get_user_by_id(contact_id)
        if not contact:
            return {"error": "Contact not found"}
        
        # Check if contact already exists
        existing_contact = UserContact.query.filter_by(
            user_id=user.user_id, 
            contact_id=contact.user_id
        ).first()
        
        if existing_contact:
            return {"error": "Contact already exists"}
        
        new_contact = UserContact(
            user_id=user.user_id,
            contact_id=contact.user_id,
            status=ContactStatusEnum.NEW,
            streak=0,
            continue_streak=True
        )
        
        db.session.add(new_contact)
        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}
    
    def change_contact_status(self, session_id, contact_id, status_str):
        user = self.user_service.get_user_by_session(session_id)
        if not user:
            return {"error": "Invalid session ID"}
        
        try:
            status = ContactStatusEnum(status_str)
        except ValueError:
            return {"error": f"Invalid status value: {status_str}"}
        
        contact = UserContact.query.filter_by(
            user_id=user.user_id, 
            contact_id=contact_id
        ).first()
        
        if not contact:
            return {"error": "Contact not found"}
        
        contact.status = status
        
        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}
    
    def get_user_contacts(self, session_id):
        user = self.user_service.get_user_by_session(session_id)
        if not user:
            return {"error": "Invalid session ID"}
        
        contacts = UserContact.query.filter_by(user_id=user.user_id).all()
        
        contact_list = []
        for contact in contacts:
            contact_user = self.user_service.get_user_by_id(contact.contact_id)
            if contact_user:
                contact_list.append({
                    "contact_id": contact.contact_id,
                    "name": contact_user.username,
                    "status": contact.status.value,
                    "streak": contact.streak,
                    "url": "https://static.spektrum.de/fm/912/f2000/205090.jpg"
                })
        
        return contact_list

    def add_contact_by_name(self, user_id, contact_name):
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            return {"error": "User not found"}

        contact = self.user_service.get_user_by_username(contact_name)
        if not contact:
            # Using Levenshtein distance (if your DB supports it)
            similar_users = User.query.order_by(
                func.levenshtein(User.username, contact_name)
            ).limit(5).all()

            suggestions = [u.username for u in similar_users
                           if u.user_id != user.user_id and func.levenshtein(u.username, contact_name) <= 3]
            if suggestions:
                return {"error": "Contact not found.", "suggestions": suggestions}
            return {"error": "Contact not found."}

        # Check if contact already exists
        existing_contact = UserContact.query.filter_by(
            user_id=user.user_id,
            contact_id=contact.user_id
        ).first()

        if existing_contact:
            return {"error": "Contact already exists"}

        new_contact = UserContact(
            user_id=user.user_id,
            contact_id=contact.user_id,
            status=ContactStatusEnum.NEW,
            streak=0,
            continue_streak=True
        )

        db.session.add(new_contact)
        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}

    def change_contact_status_by_user_id(self, user_id, contact_id, status_str):
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            return {"error": "User not found"}
        
        try:
            status = ContactStatusEnum(status_str)
        except ValueError:
            return {"error": f"Invalid status value: {status_str}"}
        
        contact = UserContact.query.filter_by(
            user_id=user.user_id, 
            contact_id=contact_id
        ).first()
        
        if not contact:
            return {"error": "Contact not found"}
        
        contact.status = status
        
        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}

    def get_user_contacts_by_user_id(self, user_id):
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            return {"error": "User not found"}
        
        contacts = UserContact.query.filter_by(user_id=user.user_id).all()
        
        contact_list = []
        for contact in contacts:
            contact_user = self.user_service.get_user_by_id(contact.contact_id)
            if contact_user:
                contact_list.append({
                    "contact_id": contact.contact_id,
                    "name": contact_user.username,
                    "status": contact.status.value,
                    "streak": contact.streak,
                    "url": "https://static.spektrum.de/fm/912/f2000/205090.jpg"
                })
        
        return contact_list
