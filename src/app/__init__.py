import os
from flask import Flask
from flask_cors import CORS

from app.extensions import db, socketio
from app.config import Config

from flask_jwt_extended import JWTManager

from datetime import datetime
from datetime import timedelta
from datetime import timezone

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["JWT_SECRET_KEY"] = "INSANE TECHNICAL DEBT"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)

    jwt = JWTManager(app)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"])
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Register blueprints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp)
    
    # Initialize WebSocket handlers
    # with app.app_context():
    #     from app.websocket import socket_handlers
    
    return app

def reset_database(app):
    """Reset database and add example data - for development only"""
    with app.app_context():
        from app.models import db
        db.session.remove()
        db.drop_all()
        db.create_all()
        
        # Insert example data
        from app.services.dummy_data import insert_example_data
        insert_example_data()
        print("Database reset completed with example data.")
