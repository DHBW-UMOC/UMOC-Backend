import enum
import uuid
from datetime import datetime
from email.policy import default

from sqlalchemy import Enum
from app import db

class GroupRoleEnum(enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"

class Group(db.Model):
    __tablename__ = 'group'

    group_id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group_name = db.Column(db.String, nullable=False)
    admin_user_id = db.Column(db.String, db.ForeignKey('user.user_id'))
    group_picture = db.Column(db.String, default='https://www.svgrepo.com/show/4552/user-groups.svg')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    admin = db.relationship('User', backref='administered_groups')
    
    def to_dict(self):
        return {
            'is_group': True,
            'contact_id': self.group_id,
            'name': self.group_name,
            'picture_url': self.group_picture,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class GroupMember(db.Model):
    __tablename__ = 'group_member'

    group_id = db.Column(db.String, db.ForeignKey('group.group_id'), primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), primary_key=True)
    encrypted_g_private_key = db.Column(db.String)
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    role = db.Column(Enum(GroupRoleEnum), nullable=False)

    group = db.relationship('Group', backref='members')
    user = db.relationship('User', backref='group_memberships')
    
    def to_dict(self):
        return {
            'group_id': self.group_id,
            'user_id': self.user_id,
            'role': self.role.value,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }
