from datetime import datetime, timedelta
from app import db
from app.models.user import User, UserContact, ContactStatusEnum
from app.models.message import Message
from app.services.user_service import UserService
from sqlalchemy import func, or_, and_

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
                    "url": contact_user.profile_picture
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
          # Find both contact relationships
        # me -> contact
        contact1 = UserContact.query.filter_by(
            user_id=user.user_id, 
            contact_id=contact_id
        ).first()
        
        # contact -> me
        contact2 = UserContact.query.filter_by(
            user_id=contact_id, 
            contact_id=user.user_id
        ).first()
        
        if not contact1:
            return {"error": "Contact not found"}
            
        # Ensure contact2 exists before trying to access its properties
        if not contact2:
            # Create reciprocal contact record if it doesn't exist
            contact_user = self.user_service.get_user_by_id(contact_id)
            if not contact_user:
                return {"error": "Contact user not found"}
                
            contact2 = UserContact(
                user_id=contact_id,
                contact_id=user.user_id,
                status=ContactStatusEnum.FRIEND  # Default status
            )
            db.session.add(contact2)          # Handle block status: blocker gets BLOCK, blocked user gets LASTWORDS
        if status == ContactStatusEnum.BLOCK:
            contact1.status = ContactStatusEnum.BLOCK
            if contact2 and contact2.status == ContactStatusEnum.BLOCK:
                pass
            else:
                contact2.status = ContactStatusEnum.LASTWORDS
            try:
                db.session.commit()
                return {"success": "The user has been blocked"}
            except Exception as e:
                db.session.rollback()
                return {"error": f"Database error: {str(e)}"}        
            
        elif status == ContactStatusEnum.UNBLOCK and contact2 and contact2.status == ContactStatusEnum.BLOCK:
            return {"error": "The user cant be unblocked because of there is another rule preventing it"}
        elif status == ContactStatusEnum.UNBLOCK and contact2 and (contact2.status == ContactStatusEnum.LASTWORDS or contact2.status == ContactStatusEnum.FBLOCKED):            # If the other user has LASTWORDS or FBLOCKED, we can unblock            contact1.status = ContactStatusEnum.FRIEND
            if contact2:
                contact2.status = ContactStatusEnum.FRIEND
            try:
                db.session.commit()
                return {"success": "The user has been unblocked"}
            except Exception as e:
                db.session.rollback()
                return {"error": f"Database error: {str(e)}"}
        elif status == ContactStatusEnum.FRIEND:
            # Check if the other user is blocked or has blocking status
            if contact2 and (contact2.status == ContactStatusEnum.FBLOCKED or 
                           contact2.status == ContactStatusEnum.LASTWORDS or 
                           contact2.status == ContactStatusEnum.BLOCK):
                return {"error": "The user cant be added as a friend because of there is another rule preventing it"}
              # If the other user already has pending friend status, make them both friends
            if contact2 and contact2.status == ContactStatusEnum.PENDINGFRIEND:
                contact1.status = ContactStatusEnum.FRIEND
                contact2.status = ContactStatusEnum.FRIEND
                try:
                    db.session.commit()
                    return {"success": "You are now friends!"}
                except Exception as e:
                    db.session.rollback()
                    return {"error": f"Database error: {str(e)}"}            # If the other user has FFRIEND status, they are responding to friend request - make both friends immediately
            elif contact2 and contact2.status == ContactStatusEnum.FFRIEND:
                # User is responding to a friend request - both become friends in this same request
                contact1.status = ContactStatusEnum.FRIEND
                contact2.status = ContactStatusEnum.FRIEND
                try:
                    db.session.commit()
                    return {"success": "You are now friends!"}
                except Exception as e:
                    db.session.rollback()
                    return {"error": f"Database error: {str(e)}"}
            else:
                # First friend request - set requesting user to pending friend, other user to FFRIEND
                contact1.status = ContactStatusEnum.PENDINGFRIEND
                # If contact2 exists, set them to FFRIEND (they received a friend request)
                if contact2:
                    contact2.status = ContactStatusEnum.FFRIEND
                try:
                    db.session.commit()
                    return {"success": "Friend request sent!"}
                except Exception as e:
                    db.session.rollback()
                    return {"error": f"Database error: {str(e)}"}
        elif status == ContactStatusEnum.UNFRIEND:
            # If the contact is blocked, we can't unfriend
            if contact2 and (contact2.status == ContactStatusEnum.BLOCK or 
                           contact2.status == ContactStatusEnum.FBLOCKED or 
                           contact2.status == ContactStatusEnum.LASTWORDS):
                return {"error": "The user cant be unfriended because of there is another rule preventing it"}
            
            # Unfriend both users
            contact1.status = ContactStatusEnum.NTCON
            if contact2:
                contact2.status = ContactStatusEnum.NTCON
        else:
            # For other status changes, just update the requesting user's contact
            contact1.status = status

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
                    "is_group": False,
                    "contact_id": contact.contact_id,
                    "name": contact_user.username,
                    "picture_url": contact_user.profile_picture,
                    "status": contact.status.value,
                    "streak": contact.streak,
                })
            self.update_streak(user.user_id, contact.contact_id)
        return contact_list
    
    def update_streak(self, user_id, contact_id):
        """Update streak if both users sent messages in the last 24 hours, reset if older."""
        try:
            today = datetime.utcnow().date()
            twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
            
            # Get both contact relationships
            contacts = UserContact.query.filter(
                or_(
                    and_(UserContact.user_id == user_id, UserContact.contact_id == contact_id),
                    and_(UserContact.user_id == contact_id, UserContact.contact_id == user_id)
                )
            ).all()
            
            if len(contacts) != 2:
                print(f"DEBUG: Contact relationship not found. Found {len(contacts)} relationships")
                return {"error": "Contact relationship not found"}
              # Check if streak was already updated today
            if contacts[0].last_streak_update == today:
                print(f"DEBUG: Streak already updated today for users {user_id} and {contact_id} - current streak: {contacts[0].streak}")
                return {
                    "success": True,
                    "streak_already_updated": True,
                    "current_streak": contacts[0].streak
                }
            
            # Check if both users sent messages to each other in last 24h
            user_sent = Message.query.filter(
                Message.sender_user_id == user_id,
                Message.recipient_user_id == contact_id,
                Message.send_at >= twenty_four_hours_ago,
                Message.is_group == False
            ).first()
            
            contact_sent = Message.query.filter(
                Message.sender_user_id == contact_id,
                Message.recipient_user_id == user_id,
                Message.send_at >= twenty_four_hours_ago,
                Message.is_group == False
            ).first()
            
            print(f"DEBUG: user_sent: {user_sent is not None}, contact_sent: {contact_sent is not None}")
            print(f"DEBUG: Calculating streak for the first time today for users {user_id} and {contact_id}")
            
            # Get both users for points update
            user = self.user_service.get_user_by_id(user_id)
            contact_user = self.user_service.get_user_by_id(contact_id)
            
            if user_sent and contact_sent:
                print(f"DEBUG: Updating streaks - before: {[c.streak for c in contacts]}")
                # Both users messaged in last 24h - increase streak and award points
                for contact in contacts:
                    contact.streak += 1
                    contact.last_streak_update = today
                
                user.points += 1
                contact_user.points += 1
                
                db.session.commit()
                print(f"DEBUG: Updated streaks - after: {[c.streak for c in contacts]}")
                return {
                    "success": True,
                    "streak_updated": True,
                    "new_streak": contacts[0].streak
                }
            else:
                print(f"DEBUG: Resetting streaks to 0")
                # Not both users messaged in last 24h - reset streaks to 0
                for contact in contacts:
                    contact.streak = 0
                    contact.last_streak_update = today
                
                db.session.commit()
                return {
                    "success": True,
                    "streak_updated": False,
                    "streak_reset": True
                }
            
        except Exception as e:
            print(f"DEBUG: Exception occurred: {str(e)}")
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}

