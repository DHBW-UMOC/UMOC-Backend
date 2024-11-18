from flask import Flask
from flask_socketio import SocketIO
from api.database.databaseManager import init_db, reset_database
from api.websockets import socketio
import api.routes as routes
import os
# from dotenv import load_dotenv


def create_app():
    app = Flask(__name__)
    
    # Load config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///umoc.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    from api.database.databaseManager import init_db
    init_db(app)
    reset_database(app)  # IMPORTANT
    socketio.init_app(app)

    # Insert dummy data
    with app.app_context():
        from api.database.insertDummyData import insert_example_data
        insert_example_data()
    
    # Register blueprints
    from api.routes import endpointApp
    app.register_blueprint(endpointApp)
    
    return app


if __name__ == '__main__':
    app = create_app()
    socketio.run(
        app,
        port=int(os.getenv('PORT', 5001)),
        debug=os.getenv('DEBUG', 'True').lower() == 'true',
        allow_unsafe_werkzeug=True
    )
