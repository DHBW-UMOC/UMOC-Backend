import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, reset_database
from app.extensions import socketio

if __name__ == '__main__':
    app = create_app()
    
    # Reset database for development (comment out for production)
    reset_database(app)
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('DEBUG', 'True').lower() == 'true',
        allow_unsafe_werkzeug=True
    )
