import enum
import uuid
from datetime import datetime
from sqlalchemy import Enum
from app import db

class ContactStatusEnum(enum.Enum):
    FRIEND = "friend"
    FFRIEND = "ffriend"  
    UNFRIEND = "unfriend"
    PENDINGFRIEND = "pending_friend"
    LASTWORDS = "last_words"
    BLOCK = "block"
    FBLOCKED = "fblocked"
    UNBLOCK = "unblock"
    NEW = "new"
    TIMEOUT = "timeout"
    NTCON = "ntcon"  # Not connected

class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(25), unique=True, index=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    profile_picture = db.Column(db.String, default="https://www.svgrepo.com/show/535711/user.svg")
    salt = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    session_id = db.Column(db.String)
    public_key = db.Column(db.String)
    encrypted_private_key = db.Column(db.String)
    is_online = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'profile_picture': self.profile_picture,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_online': self.is_online
        }

class UserContact(db.Model):
    __tablename__ = 'user_contact'

    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), primary_key=True)
    contact_id = db.Column(db.String, db.ForeignKey('user.user_id'), primary_key=True)
    status = db.Column(Enum(ContactStatusEnum), nullable=False)
    time_out = db.Column(db.DateTime)
    streak = db.Column(db.Integer, default=0)
    continue_streak = db.Column(db.Boolean, default=True)
    
    user = db.relationship('User', foreign_keys=[user_id], backref='contacts')
    contact = db.relationship('User', foreign_keys=[contact_id])
    
    def to_dict(self):
        return {
            'contact_id': self.contact_id,
            'name': self.contact.username if self.contact else None,
            'status': self.status.value,
            'streak': self.streak,
            'profile_picture': self.user.profile_picture
        }
