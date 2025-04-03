from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# Create extensions objects
db = SQLAlchemy()
socketio = SocketIO()
