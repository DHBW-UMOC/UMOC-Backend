from flask_socketio import SocketIO, emit, join_room, leave_room
from .database.models import User, Message

socketio = SocketIO()


###########################
## WEBSOCKET ENDPOINTS
###########################
@socketio.on('connect')
def handle_connect():
    pass


@socketio.on('disconnect')
def handle_disconnect():
    pass
