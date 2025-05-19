import enum
from sqlalchemy import Enum
from app import db

class ItemTypeEnum(enum.Enum):
    MUTE = "mute"
    LIGHTMODE = "lightmode"
    KICK = "kick"

class Inventory(db.Model):
    __tablename__ = 'inventory'

    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), primary_key=True)
    item_type = db.Column(Enum(ItemTypeEnum), primary_key=True)
    item_count = db.Column(db.Integer, nullable=False, default=0)

    user = db.relationship('User', backref='inventories')
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'item_type': self.item_type.value,
            'item_count': self.item_count
        }
