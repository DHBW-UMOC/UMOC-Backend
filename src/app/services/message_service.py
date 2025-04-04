from datetime import datetime
from sqlalchemy import or_, and_, func
import uuid

from app.extensions import db
from app.models.message import Message, MessageRead, MessageTypeEnum
from app.models.user import User
from app.models.group import Group, GroupMember


class MessageService:
    """Service to handle message-related operations."""
    
    def save_message(self, session_id, recipient_id, content, is_group=False, message_type=MessageTypeEnum.TEXT):
        """Save a new message to the database."""
        # First, get the sender user
        user = User.query.filter_by(session_id=session_id).first()
        if not user:
            return {"error": "Invalid session ID"}
        
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
        db.session.commit()
        
        return {"message_id": message.message_id}

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
                    Message.is_group == True,
                    Message.recipient_user_id == chat_id
                ).order_by(Message.send_at.desc())
                
            else:
                # For direct messages
                query = Message.query.filter(
                    Message.is_group == False,
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
                    Message.is_group == True,
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
                    Message.is_group == False,
                    Message.recipient_user_id == user_id,
                    Message.sender_user_id == chat_id,
                    ~Message.message_id.in_(
                        db.session.query(MessageRead.message_id).filter(
                            MessageRead.reader_id == user_id
                        )
                    )
                )
            
            return query.scalar() or 0
            
        except Exception as e:
            return 0
