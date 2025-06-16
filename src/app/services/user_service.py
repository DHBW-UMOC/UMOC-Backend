import uuid
from datetime import datetime
import time
from app import db
from app.models.user import User

from app.models.user import UserContact


class UserService:
    def register_user(self, username, password, profile_pic, public_key=""):
        # Check if user already exists
        t0 = time.time()
        existing_user = User.query.filter_by(username=username).first()
        print("Check existing user:", time.time() - t0)

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
        try:
            t1 = time.time()
            db.session.add(new_user)
            db.session.commit()
            print("Insert + commit:", time.time() - t1)
            print("Total register time:", time.time() - t0)

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
        
    def change_username(self, user_id, new_username):
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return {"error": "User not found"}
        user.username = new_username
        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred: {e}"}
        
    def change_profile_picture(self, user_id, new_profile_picture):
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return {"error": "User not found"}
        user.profile_picture = new_profile_picture
        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred: {e}"}
        
    def change_password(self, user_id, old_password, new_password):
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return {"error": "User not found"}
        if user.password != old_password:
            return {"error": "Old password is incorrect"}
        
        user.password = new_password
        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred: {e}"}
    
    def get_user_by_session(self, session_id):
        return User.query.filter_by(session_id=session_id).first()
    
    def get_user_by_id(self, user_id):
        return User.query.filter_by(user_id=user_id).first()
    
    def get_all_users_by_word(self, word):
        try:
            users = User.query.filter(User.username.ilike(f"{word}%")).limit(20).all()
            result = []
            for user in users:
                result.append({
                    "user_id": user.user_id,
                    "username": user.username,
                    "profile_picture": user.profile_picture
                })
            return result
        except Exception as e:
            return {"error": f"An unexpected error occurred: {e}"}
        
    
    def get_user_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def does_user_exist(self, user_id):
        return User.query.filter_by(user_id=user_id).first() is not None

    def get_user_streak(self, user_id):
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return {"error": "User not found"}

        streak = 0
        contacts = UserContact.query.filter_by(user_id=user.user_id).all()
        for contact in contacts:
            streak += contact.streak
        return streak
    
    def get_user_points(self, user_id):
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return {"error": "User not found"}
        return user.points
    
    def update_streak(user_id):
        pass


