import enum
import uuid
from datetime import datetime
from sqlalchemy import Enum
from app.extensions import db

class MessageTypeEnum(enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    ITEM = "item"

class Message(db.Model):
    __tablename__ = 'message'

    message_id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    recipient_user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    encrypted_content = db.Column(db.String, nullable=False)
    type = db.Column(Enum(MessageTypeEnum), nullable=False)
    send_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    is_group = db.Column(db.Boolean, default=False)

    sender = db.relationship('User', foreign_keys=[sender_user_id], backref='messages_sent')
    recipient = db.relationship('User', foreign_keys=[recipient_user_id], backref='messages_received')
    
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

    message_id = db.Column(db.String, db.ForeignKey('message.message_id'), primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), primary_key=True)
    
    message = db.relationship('Message', backref='statuses')
    user = db.relationship('User', backref='message_statuses')
