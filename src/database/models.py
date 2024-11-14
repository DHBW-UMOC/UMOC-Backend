from sqlalchemy import Enum
from databaseManager import db
import uuid
from datetime import datetime
import enum

class ContactStatusEnum(enum.Enum):
    FRIEND = "friend"
    LASTWORDS = "last_words"
    BLOCKED = "blocked"
    NEW = "new"
    TIMEOUT = "timeout"


class ItemTypeEnum(enum.Enum):
    MUTE = "mute"
    LIGHTMODE = "lightmode"
    KICK = "kick"


class GroupRoleEnum(enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"


class MessageTypeEnum(enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    ITEM = "item"


class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    salt = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    session_id = db.Column(db.String)
    public_key = db.Column(db.String)
    encrypted_private_key = db.Column(db.String)
    is_online = db.Column(db.Boolean, default=False)

    contacts = db.relationship('UserContact', foreign_keys='UserContact.user_id', backref='user', lazy=True)
    inventories = db.relationship('Inventory', backref='user', lazy=True)
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_user_id', backref='sender', lazy=True)
    messages_received = db.relationship('Message', foreign_keys='Message.recipient_user_id', backref='recipient',
                                        lazy=True)
    group_memberships = db.relationship('GroupMember', backref='user', lazy=True)
    message_statuses = db.relationship('GMessageStatus', backref='user', lazy=True)


class UserContact(db.Model):
    __tablename__ = 'user_contact'

    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), primary_key=True)
    contact_id = db.Column(db.String, db.ForeignKey('user.user_id'), primary_key=True)
    status = db.Column(Enum(ContactStatusEnum), nullable=False)
    time_out = db.Column(db.DateTime)
    streak = db.Column(db.Integer)
    continue_streak = db.Column(db.Boolean, default=True)


class Inventory(db.Model):
    __tablename__ = 'inventory'

    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), primary_key=True)
    item_type = db.Column(Enum(ItemTypeEnum), primary_key=True)
    item_count = db.Column(db.Integer, nullable=False)


class Group(db.Model):
    __tablename__ = 'group'

    group_id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group_name = db.Column(db.String, nullable=False)
    admin_user_id = db.Column(db.String, db.ForeignKey('user.user_id'))
    public_key = db.Column(db.String)
    create_at = db.Column(db.DateTime, nullable=False)

    members = db.relationship('GroupMember', backref='group', lazy=True)


class GroupMember(db.Model):
    __tablename__ = 'group_member'

    group_id = db.Column(db.String, db.ForeignKey('group.group_id'), primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), primary_key=True)
    encrypted_g_private_key = db.Column(db.String)
    joined_at = db.Column(db.DateTime, nullable=False)
    role = db.Column(Enum(GroupRoleEnum), nullable=False)


class Message(db.Model):
    __tablename__ = 'message'

    message_id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    recipient_user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    encrypted_content = db.Column(db.String, nullable=False)
    type = db.Column(Enum(MessageTypeEnum), nullable=False)
    send_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime)
    is_group = db.Column(db.Boolean, default=False)

    statuses = db.relationship('GMessageStatus', backref='message', lazy=True)


class GMessageStatus(db.Model):
    __tablename__ = 'g_message_status'

    message_id = db.Column(db.String, db.ForeignKey('message.message_id'), primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), primary_key=True)
