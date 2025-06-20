from datetime import datetime, timedelta
from app import db
from app.models.items import Item, ActiveItems, Inventory
from app.services.user_service import UserService


class ItemService:

    def __init__(self):
        self.user_service = UserService()

    def create_item(self, name, price):
        new_item = Item(name=name, price=price)
        db.session.add(new_item)
        return new_item

    def buy_item(self, item_name, user_id):
        """user buys item and add to inventory"""
        item = Item.query.filter_by(name=item_name).first()
        user = self.user_service.get_user_by_id(user_id)

        if not item:
            return {"error": "Item not found"}

        # TODO: Check if user has enough Points to buy the item
        if user.points < item.price:
            return {"error": "Not enough points to buy this item"}

        inventory_item = Inventory.query.filter_by(item_id=item.id, user_id=user_id).first()
        if inventory_item:
            #decrease user points
            user.points -= item.price
            inventory_item.quantity += 1
        else:
            inventory_item = Inventory(item_id=item.id, user_id=user_id, quantity=1)
            #decrease user points
            user.points -= item.price
            db.session.add(inventory_item)

        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}

    def use_item(self, item_name, user_id, to_user_id):
        """user uses item from inventory. This will create an active item"""
        item = Item.query.filter_by(name=item_name).first()
        if not item:
            return {"error": "Item not found"}, None

        inventory_item = Inventory.query.filter_by(item_id=item.id, user_id=user_id).first()
        if not inventory_item or inventory_item.quantity <= 0:
            return {"error": "Item not in inventory or quantity is zero"}, None

        if ActiveItems.query.filter_by(item=item.name, user_id=to_user_id) \
                .filter(ActiveItems.active_until > datetime.utcnow() + timedelta(hours=2)).first():
            return {"error": "Item already active for this user"}, None

        active_item = ActiveItems(
            item=item.name,
            user_id=to_user_id,
            send_by_user_id=user_id,
            active_until=datetime.utcnow() + timedelta(hours=2) + timedelta(minutes=1) # Active for 1 Minute
        )
        db.session.add(active_item)

        inventory_item.quantity -= 1
        if inventory_item.quantity <= 0:
            db.session.delete(inventory_item)

        try:
            db.session.commit()
            return {"success": True}, datetime.utcnow() + timedelta(hours=2) + timedelta(minutes=1)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}, None

    def get_item_list(self):
        """Get list of all items"""
        items = Item.query.all()
        return [item.to_dict() for item in items]
        
    def get_active_items(self, user_id):
        """Get all active items for a user that are still active"""
        active_items = ActiveItems.query.filter(
            ActiveItems.user_id == user_id,
            ActiveItems.active_until > datetime.utcnow() + timedelta(hours=2)  # Active for at least 1 minute
        ).all()
        return [item.to_dict() for item in active_items]

    def get_inventory(self, user_id):
        """Get inventory for a user"""
        inventory = Inventory.query.filter_by(user_id=user_id).all()
        return [item.to_dict() for item in inventory]

    def delete_item(self, item_name):
        """Delete an item from the database"""
        item = Item.query.filter_by(name=item_name).first()
        if not item:
            return {"error": "Item not found"}

        db.session.delete(item)
        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}

    def delete_unacive_items(self):
        """Delete all active items that are no longer active"""
        now = datetime.utcnow()
        deleted_count = ActiveItems.query.filter(ActiveItems.active_until < now).delete()
        try:
            db.session.commit()
            return {"success": True, "deleted_count": deleted_count}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}

    def reset_items(self):
        """Reset items to default state"""
        db.session.query(Item).delete()
        db.session.query(ActiveItems).delete()
        db.session.query(Inventory).delete()

        # Add default items
        self.create_item("timeout", 5)
        self.create_item("alt_background", 5)
        self.create_item("show_ads", 2)
        self.create_item("flashbang", 1)

        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}

