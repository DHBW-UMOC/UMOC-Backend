from datetime import datetime
import uuid
from sqlalchemy import or_, and_, func

from app import db
from app.models.message import Message, MessageRead, MessageTypeEnum
from app.models.user import User
from app.models.group import Group, GroupMember


class MessageService:
    """Service to handle message-related operations."""
    
    def save_message(self, user_id, recipient_id, content, is_group=False, message_type=MessageTypeEnum.TEXT):
        """Save a new message to the database."""
        # First, get the sender user
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return {"error": "Invalid user ID"}
        
        # Check if recipient exists
        if is_group:
            recipient = Group.query.get(recipient_id)
            if not recipient:
                return {"error": "Group not found"}
                
            # Check if sender is a member of the group
            member = GroupMember.query.filter_by(group_id=recipient_id, user_id=user.user_id).first()
            if not member:
                return {"error": "You are not a member of this group"}
        else:
            recipient = User.query.get(recipient_id)
            if not recipient:
                return {"error": "Recipient not found"}
        
        # Create new message
        message = Message(
            message_id=str(uuid.uuid4()),
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
            return {"message_id": message.message_id}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}

    def get_messages_with_groups(self, user_id, group_id, page=None):
        """
        Get messages between a user and a group.

        Args:
            user_id: The ID of the user
            group_id: The ID of the group
            page: Optional. Page number for pagination (default: None, returns all messages)

        Returns:
            tuple: JSON response and status code
        """
        try:
            spec_user = User.query.filter_by(user_id=user_id).first()
            group = Group.query.get(group_id)
            member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()

            if not spec_user:
                return {"error": "Invalid user ID"}, 400
            if not group:
                return {"error": "Group not found"}, 400
            if not member:
                return {"error": "You are not a member of this group"}, 403

            # Query messages in the group
            base_query = Message.query.filter(
                Message.recipient_user_id == group_id,
                Message.is_group.is_(True)
            ).order_by(Message.send_at)

            # Pagination logic
            if page is not None:
                page = int(page)
                per_page = 20
                messages = base_query.limit(per_page).offset((page - 1) * per_page).all()
            else:
                messages = base_query.all()

            # Format the messages for response
            formatted_messages = []
            for msg in messages:
                # Get sender info
                sender = User.query.get(msg.sender_user_id)
                sender_username = sender.username if sender else "Unknown User"

                message_data = {
                    'message_id': msg.message_id,
                    'sender_user_id': msg.sender_user_id,
                    'sender_username': sender_username,
                    'recipient_id': msg.recipient_user_id,
                    'content': msg.encrypted_content,
                    'type': msg.type.value if hasattr(msg.type, 'value') else 'text',
                    'timestamp': msg.send_at.isoformat() if msg.send_at else None,
                }
                formatted_messages.append(message_data)

            return {"messages": formatted_messages}, 200

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def get_messages_with_contact(self, user_id, contact_id, page=None):
        """
        Get messages between a user and their contact.

        Args:
            user_id: The ID of the user
            contact_id: The ID of the contact
            page: Optional. Page number for pagination (default: None, returns all messages)

        Returns:
            tuple: JSON response and status code
        """
        try:
            # First, get the user by user_id
            spec_user = User.query.filter_by(user_id=user_id).first()
            if not spec_user:
                return {"error": "Invalid user ID"}, 400

            # Check if the contact exists
            contact = User.query.get(contact_id)
            if not contact:
                return {"error": "Contact not found"}, 400

            # Query messages between the user and the contact (in both directions)
            base_query = Message.query.filter(
                or_(
                    and_(Message.sender_user_id == spec_user.user_id, Message.recipient_user_id == contact_id),
                    and_(Message.sender_user_id == contact_id, Message.recipient_user_id == spec_user.user_id)
                )
            ).order_by(Message.send_at)

            # Pagination logic
            if page is not None:
                page = int(page)
                per_page = 20
                messages = base_query.limit(per_page).offset((page - 1) * per_page).all()
            else:
                messages = base_query.all()

            # Format the messages for response
            formatted_messages = []
            for msg in messages:
                # Get sender info
                sender = User.query.get(msg.sender_user_id)
                sender_username = sender.username if sender else "Unknown User"

                message_data = {
                    'message_id': msg.message_id,
                    'sender_user_id': msg.sender_user_id,
                    'sender_username': sender_username,
                    'recipient_id': msg.recipient_user_id,
                    'content': msg.encrypted_content,
                    'type': msg.type.value if hasattr(msg.type, 'value') else 'text',
                    'timestamp': msg.send_at.isoformat() if msg.send_at else None,
                }
                formatted_messages.append(message_data)

            return {"messages": formatted_messages}, 200

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def get_chat_messages(self, user_id, chat_id, is_group=False, page=1, page_size=20):
        """Get paginated messages for a chat."""
        try:
            # Calculate offset based on page and page_size
            offset = (page - 1) * page_size

            if is_group:
                # For group chats
                # First check if user is part of this group
                member = GroupMember.query.filter_by(group_id=chat_id, user_id=user_id).first()
                if not member:
                    return {"error": "You are not a member of this group"}
                
                # Get group messages
                query = Message.query.filter(
                    Message.is_group is True,
                    Message.recipient_user_id == chat_id
                ).order_by(Message.send_at.desc())
                
            else:
                # For direct messages
                query = Message.query.filter(
                    Message.is_group is False,
                    or_(
                        and_(Message.sender_user_id == user_id, Message.recipient_user_id == chat_id),
                        and_(Message.sender_user_id == chat_id, Message.recipient_user_id == user_id)
                    )
                ).order_by(Message.send_at.desc())
            
            # Count total messages for pagination info
            total_messages = query.count()
            total_pages = (total_messages + page_size - 1) // page_size  # Ceiling division
            
            # Get the messages for the current page
            messages = query.limit(page_size).offset(offset).all()
            
            # Format messages for response
            formatted_messages = []
            for msg in messages:
                # Get sender info (using the relationship)
                sender = msg.sender
                
                # For recipient info, we need to handle user vs group differently
                # since we don't have a direct relationship anymore
                if msg.is_group:
                    recipient = Group.query.get(msg.recipient_user_id)
                    recipient_name = recipient.name if recipient else "Unknown Group"
                else:
                    recipient = User.query.get(msg.recipient_user_id)
                    recipient_name = recipient.username if recipient else "Unknown User"
                
                message_data = {
                    'message_id': msg.message_id,
                    'sender_id': msg.sender_user_id,
                    'sender_username': sender.username if sender else "Unknown",
                    'recipient_id': msg.recipient_user_id,
                    'recipient_name': recipient_name,
                    'content': msg.encrypted_content,
                    'type': msg.type.value,
                    'timestamp': msg.send_at.isoformat(),
                    'is_group': msg.is_group,
                    'read': self.is_message_read(msg.message_id, user_id)
                }
                formatted_messages.append(message_data)
            
            return {
                "messages": formatted_messages,
                "total_messages": total_messages,
                "total_pages": total_pages
            }
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}

    def get_last_message_date_for_contact(self, user_id, contact_id) -> str:
        """Get the last message exchanged with a contact."""
        try:
            # Get the last message between user and contact
            last_message = Message.query.filter(
                or_(
                    and_(Message.sender_user_id == user_id, Message.recipient_user_id == contact_id),
                    and_(Message.sender_user_id == contact_id, Message.recipient_user_id == user_id)
                )
            ).order_by(Message.send_at.desc()).first()

            if not last_message:
                return "2001-09-11T12:46:00Z"

            return last_message.send_at.isoformat()

        except Exception as _:
            db.session.rollback()
            return "2001-09-11T12:46:00Z"

    def mark_as_read(self, message_id, reader_id):
        """Mark a message as read by a user."""
        try:
            # Check if message exists
            message = Message.query.get(message_id)
            if not message:
                return {"error": "Message not found"}
            
            # Check if user is authorized to read this message
            if not message.is_group and message.recipient_user_id != reader_id and message.sender_user_id != reader_id:
                return {"error": "Unauthorized"}
            
            if message.is_group:
                # Check if user is a member of the group
                member = GroupMember.query.filter_by(
                    group_id=message.recipient_user_id, 
                    user_id=reader_id
                ).first()
                if not member:
                    return {"error": "Not a member of this group"}
            
            # Don't mark sender's own messages as read
            if message.sender_user_id == reader_id:
                return {"success": True}
                
            # Check if already marked as read
            existing = MessageRead.query.filter_by(
                message_id=message_id,
                reader_id=reader_id
            ).first()
            
            if not existing:
                # Create new read receipt
                read_receipt = MessageRead(
                    message_id=message_id,
                    reader_id=reader_id,
                    read_at=datetime.utcnow()
                )
                db.session.add(read_receipt)
                db.session.commit()
            
            return {"success": True}
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}
    
    def is_message_read(self, message_id, user_id):
        """Check if a message has been read by a user."""
        read = MessageRead.query.filter_by(
            message_id=message_id,
            reader_id=user_id
        ).first()
        
        return read is not None
    
    def get_unread_count(self, user_id, chat_id, is_group=False):
        """Get count of unread messages in a chat."""
        try:
            if is_group:
                # Get unread messages for group
                query = db.session.query(func.count(Message.message_id)).filter(
                    Message.is_group is True,
                    Message.recipient_user_id == chat_id,
                    Message.sender_user_id != user_id,
                    ~Message.message_id.in_(
                        db.session.query(MessageRead.message_id).filter(
                            MessageRead.reader_id == user_id
                        )
                    )
                )
            else:
                # Get unread messages for direct chat
                query = db.session.query(func.count(Message.message_id)).filter(
                    Message.is_group is False,
                    Message.recipient_user_id == user_id,
                    Message.sender_user_id == chat_id,
                    ~Message.message_id.in_(
                        db.session.query(MessageRead.message_id).filter(
                            MessageRead.reader_id == user_id
                        )
                    )
                )
            
            return query.scalar() or 0
            
        except Exception as _:
            return 0


    def delete_message(self, user_id, message_id):
        """Delete a message by its ID."""
        try:
            # Check if message exists
            print(f"Attempting to delete message with ID: {message_id} by user {user_id}")
            message = Message.query.filter_by(message_id=message_id).first()
            if not message:
                return {"error": "Message not found"}

            # Delete the message
            message.type = MessageTypeEnum.DELETED_TEXT
            db.session.commit()

            return {"success": True}

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}

    def get_recipient_id_by_message_id(self, message_id):
        """Get the recipient ID for a given message ID."""
        try:
            message = Message.query.filter_by(message_id=message_id).first()
            if not message:
                return None

            return message.recipient_user_id

        except Exception as e:
            db.session.rollback()
            return None
