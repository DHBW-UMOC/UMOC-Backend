from datetime import datetime
from app import db


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Item {self.name} ({self.price} Gold)>"

    def to_dict(self):
        return {
            'item_name': self.name,
            'price': self.price,
        }


class ActiveItems(db.Model):
    __tablename__ = 'active_items'

    id = db.Column(db.Integer, primary_key=True)

    item = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    send_by_user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    active_until = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'item_name': self.item,
            'active_until': self.active_until.isoformat(),
        }

class Inventory(db.Model):
    __tablename__ = 'inventory'

    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    __table_args__ = (
        db.PrimaryKeyConstraint('item_id', 'user_id'),
    )

    def to_dict(self):
        return {
            'item_name': Item.query.get(self.item_id).name if self.item_id else None,
            'user_id': self.user_id,
            'quantity': self.quantity,
        }