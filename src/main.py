import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import reset_database, create_app
from app.websocket.websockets import socketio, init_websockets

app = create_app()
init_websockets(app)

if __name__ == '__main__':
    # Reset database for development (comment out for production)
    reset_database(app)

    socketio.run(
        app,
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('DEBUG', 'True').lower() == 'true',
        allow_unsafe_werkzeug=True
    )

