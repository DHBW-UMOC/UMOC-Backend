import os
from flask import Flask
from flask_cors import CORS

from app.extensions import db, socketio
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["JWT_SECRET_KEY"] = "INSANE TECHNICAL DEBT"
    
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
