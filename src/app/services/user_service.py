import uuid
from datetime import datetime
from app.extensions import db
from app.models.user import User

class UserService:
    def register_user(self, username, password, public_key=""):
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return {"error": "Username already exists"}  # Conflict
        
        # In a real application, password would be hashed with salt
        new_user = User(
            username=username,
            password=password,
            salt="",  # In production, generate a random salt
            created_at=datetime.utcnow(),
            public_key=public_key
        )
        
        db.session.add(new_user)
        try:
            db.session.commit()
            return {"success": True, "user_id": new_user.user_id}
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred during registration: {e}"}  # Internal error
    
    def login_user(self, username, password):
        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            return {"error": "Invalid username or password"}  # Unauthorized
        
        # Generate a new session ID
        session_id = str(uuid.uuid4())
        user.session_id = session_id
        user.is_online = True
        
        try:
            db.session.commit()
            return {"success": True, "session_id": session_id, "user_id": user.user_id}
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred during login: {e}"}  # Internal error
    
    def logout_user(self, session_id):
        user = User.query.filter_by(session_id=session_id).first()
        if not user:
            return {"error": "Session not found"}  # Not Found
        
        user.session_id = None
        user.is_online = False
        
        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred during logout: {e}"}  # Internal error
    
    def logout_user_by_user_id(self, user_id):
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return {"error": "User not found"}  # Not Found
        
        user.session_id = None
        user.is_online = False
        
        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred during logout: {e}"}  # Internal error
    
    def get_user_by_session(self, session_id):
        return User.query.filter_by(session_id=session_id).first()
    
    def get_user_by_id(self, user_id):
        return User.query.filter_by(user_id=user_id).first()
    
    def get_user_by_username(self, username):
        return User.query.filter_by(username=username).first()
