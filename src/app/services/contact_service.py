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
        today = datetime.utcnow().date()
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        
        # Check contact streaks in bulk instead of one by one
        contact_ids_to_check = [c.contact_id for c in contacts]
        
        # Process in small batches to avoid overwhelming the system
        batch_size = 5
        updated_streaks = {}
        
        for i in range(0, len(contact_ids_to_check), batch_size):
            batch = contact_ids_to_check[i:i+batch_size]
            
            # For each contact in batch, check if they need streak validation
            for contact_id in batch:
                # Only validate if it hasn't been validated today
                contact = next((c for c in contacts if c.contact_id == contact_id), None)
                if contact and (not hasattr(contact, 'last_streak_update') or contact.last_streak_update != today):
                    self.check_streak_validity(user_id, contact_id, twenty_four_hours_ago)
        
        # Refresh contacts after potential updates
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
        return contact_list
    
    def update_streak(self, user_id, contact_id):
        """Update streak if both users sent messages in the last 24 hours, reset if older.
        
        This is called when a message is sent to ensure streaks are updated in real-time.
        """
        try:
            today = datetime.utcnow().date()
            twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
            
            # Validate streak status first
            self.check_streak_validity(user_id, contact_id, twenty_four_hours_ago)
            
            # Get contact relationships that exist (we won't create missing ones)
            contacts = UserContact.query.filter(
                or_(
                    and_(UserContact.user_id == user_id, UserContact.contact_id == contact_id),
                    and_(UserContact.user_id == contact_id, UserContact.contact_id == user_id)
                )
            ).all()
            
            if not contacts:
                print(f"DEBUG: No contact relationships found between users {user_id} and {contact_id}")
                return {"error": "Contact relationship not found"}
            
            if len(contacts) < 2:
                print(f"DEBUG: Found {len(contacts)} contact relationship(s). Continuing with existing relationship(s).")
            
            # Get the latest messages between the users
            latest_user_message = Message.query.filter(
                Message.sender_user_id == user_id,
                Message.recipient_user_id == contact_id,
                Message.is_group == False
            ).order_by(Message.send_at.desc()).first()
            
            latest_contact_message = Message.query.filter(
                Message.sender_user_id == contact_id,
                Message.recipient_user_id == user_id,
                Message.is_group == False
            ).order_by(Message.send_at.desc()).first()
            
            # Log the latest messages for debugging
            if latest_user_message:
                user_msg_time = latest_user_message.send_at
                print(f"DEBUG: Latest message from user {user_id} was at {user_msg_time}")
            if latest_contact_message:
                contact_msg_time = latest_contact_message.send_at
                print(f"DEBUG: Latest message from contact {contact_id} was at {contact_msg_time}")
            
            # Check if both users have messages and if they're within 24 hours of each other
            both_recent_messages = (
                latest_user_message and 
                latest_contact_message and
                latest_user_message.send_at >= twenty_four_hours_ago and
                latest_contact_message.send_at >= twenty_four_hours_ago
            )
            
            # Get both users for points update
            user = self.user_service.get_user_by_id(user_id)
            contact_user = self.user_service.get_user_by_id(contact_id)
            
            if not user or not contact_user:
                print(f"DEBUG: Could not find one or both users. User: {user is not None}, Contact: {contact_user is not None}")
                return {"error": "One or both users not found"}
            
            # Check if points field exists on user model
            has_points = hasattr(user, 'points')
            
            # Check if we've already updated the streak today and had a positive streak
            # Only prevent updating if streak was already increased today
            streak_established_today = any(
                hasattr(c, 'last_streak_update') and 
                c.last_streak_update == today and
                c.streak > 0
                for c in contacts
            )
            
            if streak_established_today and both_recent_messages:
                # If we already established a streak today and both have messaged recently,
                # return the current streak without further processing
                streak_value = next((c.streak for c in contacts), 0)
                print(f"DEBUG: Streak already established today at {streak_value}. No further updates needed.")
                return {
                    "success": True,
                    "streak_already_updated": True,
                    "current_streak": streak_value
                }
            
            if both_recent_messages:
                print(f"DEBUG: Both users have messaged in last 24h. Updating streaks...")
                print(f"DEBUG: Current streaks: {[getattr(c, 'streak', 0) for c in contacts]}")
                
                # Both users messaged recently - increase streak and award points
                for contact in contacts:
                    contact.streak += 1
                    contact.last_streak_update = today
                
                # Only update points if the field exists
                if has_points:
                    user.points = getattr(user, 'points', 0) + 1
                    contact_user.points = getattr(contact_user, 'points', 0) + 1
                
                db.session.commit()
                print(f"DEBUG: Updated streaks - now: {[c.streak for c in contacts]}")
                return {
                    "success": True,
                    "streak_updated": True,
                    "new_streak": contacts[0].streak
                }
            else:
                # Don't reset streaks on every check - only reset if it's been 24+ hours since last message 
                # AND we haven't already reset today
                should_reset = all(
                    not hasattr(c, 'last_streak_update') or c.last_streak_update != today
                    for c in contacts
                )
                
                if should_reset:
                    print(f"DEBUG: Resetting streaks to 0 - no recent message exchange")
                    # Not both users messaged recently - reset streaks to 0
                    for contact in contacts:
                        contact.streak = 0
                        contact.last_streak_update = today
                    
                    db.session.commit()
                    return {
                        "success": True,
                        "streak_updated": False,
                        "streak_reset": True
                    }
                else:
                    print(f"DEBUG: No streak update needed")
                    return {
                        "success": True,
                        "streak_updated": False
                    }
            
        except Exception as e:
            print(f"DEBUG: Exception occurred: {str(e)}")
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}
            
        except Exception as e:
            print(f"DEBUG: Exception occurred: {str(e)}")
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}
    
    def check_streak_validity(self, user_id, contact_id, twenty_four_hours_ago=None):
        """Check if a streak is still valid without trying to increment it.
        This is used when loading contacts to invalidate streaks if users haven't messaged recently.
        """
        try:
            if twenty_four_hours_ago is None:
                twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
            
            today = datetime.utcnow().date()
            
            # Get contact relationships that exist (we won't create missing ones)
            contacts = UserContact.query.filter(
                or_(
                    and_(UserContact.user_id == user_id, UserContact.contact_id == contact_id),
                    and_(UserContact.user_id == contact_id, UserContact.contact_id == user_id)
                )
            ).all()
            
            if not contacts:
                print(f"DEBUG: No contact relationships found between users {user_id} and {contact_id}")
                return False
            
            # Check if we've already validated the streak today
            already_validated_today = any(
                hasattr(c, 'last_streak_update') and c.last_streak_update == today
                for c in contacts
            )
            
            if already_validated_today:
                return True  # Already validated today, no need to check again
            
            # Get the latest messages between the users
            latest_user_message = Message.query.filter(
                Message.sender_user_id == user_id,
                Message.recipient_user_id == contact_id,
                Message.is_group == False
            ).order_by(Message.send_at.desc()).first()
            
            latest_contact_message = Message.query.filter(
                Message.sender_user_id == contact_id,
                Message.recipient_user_id == user_id,
                Message.is_group == False
            ).order_by(Message.send_at.desc()).first()
            
            # If either user hasn't sent a message in the last 24 hours
            # AND the streak hasn't been reset today, reset it
            both_recent_messages = (
                latest_user_message and 
                latest_contact_message and
                latest_user_message.send_at >= twenty_four_hours_ago and
                latest_contact_message.send_at >= twenty_four_hours_ago
            )
            
            if not both_recent_messages:
                # If the streak is positive and we haven't reset it today,
                # reset it to 0
                for contact in contacts:
                    if contact.streak > 0:
                        print(f"DEBUG: Resetting streak for {user_id} and {contact_id} - no recent message exchange")
                        contact.streak = 0
                    contact.last_streak_update = today
                
                db.session.commit()
                return False
            
            # Mark as validated today but don't increment
            for contact in contacts:
                contact.last_streak_update = today
            
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"DEBUG: Exception in check_streak_validity: {str(e)}")
            db.session.rollback()
            return False

