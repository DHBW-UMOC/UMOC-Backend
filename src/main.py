from flask import Flask
from flask_socketio import SocketIO
from database.databaseManager import init_db
from api.websockets import socketio
import os
# from dotenv import load_dotenv


def create_app():
    # Load environment variables
    # load_dotenv()

    # Create Flask app
    app = Flask(__name__)

    # Configure app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///umoc.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    init_db(app)
    socketio.init_app(app)

    return app


if __name__ == '__main__':
    app = create_app()
    socketio.run(
        app,
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('DEBUG', 'True').lower() == 'true'
    )