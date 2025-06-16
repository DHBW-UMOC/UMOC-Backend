import enum
import uuid
from datetime import datetime
from sqlalchemy import Enum, Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app import db

class MessageTypeEnum(enum.Enum):
    TEXT = "text"
    DELETED_TEXT = "deleted_text"
    IMAGE = "image"
    ITEM = "item"
    LOCATION = "location"
    AUDIO = "audio"
    VIDEO = "video"

class Message(db.Model):
    __tablename__ = 'message'

    message_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_user_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    recipient_user_id = Column(String, nullable=False)
    encrypted_content = Column(String, nullable=False)
    type = Column(Enum(MessageTypeEnum), default=MessageTypeEnum.TEXT)
    send_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_group = Column(Boolean, default=False)

    sender = relationship('User', foreign_keys=[sender_user_id], backref='messages_sent')
    
    # Remove the problematic recipient relationship that has no proper foreign key
    # recipient = relationship('User', foreign_keys=[recipient_user_id], backref='messages_received')
    
    read_receipts = relationship("MessageRead", back_populates="message", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'message_id': self.message_id,
            'sender_user_id': self.sender_user_id,
            'content': self.encrypted_content,
            'type': self.type.value,
            'send_at': self.send_at.isoformat() if self.send_at else None,
            'is_group': self.is_group
        }

class GMessageStatus(db.Model):
    __tablename__ = 'g_message_status'

    message_id = Column(String, ForeignKey('message.message_id'), primary_key=True)
    user_id = Column(String, ForeignKey('user.user_id'), primary_key=True)
    
    message = relationship('Message', backref='statuses')
    user = relationship('User', backref='message_statuses')

class MessageRead(db.Model):
    """Tracks which users have read which messages."""
    __tablename__ = 'message_read'
    
    message_id = Column(String, ForeignKey('message.message_id', ondelete="CASCADE"), primary_key=True)
    reader_id = Column(String, ForeignKey('user.user_id', ondelete="CASCADE"), primary_key=True)
    read_at = Column(DateTime, nullable=False)
    
    # Relationships
    message = relationship("Message", back_populates="read_receipts")
    reader = relationship("User")
    
    def __repr__(self):
        return f"<MessageRead message={self.message_id} reader={self.reader_id}>"
