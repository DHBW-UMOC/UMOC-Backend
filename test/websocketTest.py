import socketio
import time
import requests
from datetime import datetime


class WebSocketTester:
    def __init__(self, server_url='http://127.0.0.1:5000'):
        self.sio = socketio.Client(logger=True, engineio_logger=True)
        self.server_url = server_url
        self.session_id = None

        @self.sio.on('connect')
        def on_connect():
            print("Connected to server!")

        @self.sio.on('connect_error')
        def on_connect_error(data):
            print(f"Connection error: {data}")

        @self.sio.on('disconnect')
        def on_disconnect():
            print("Disconnected from server!")

        @self.sio.on('new_message')
        def on_message(data):
            print(f"\nReceived message: {data}")

        @self.sio.on('user_status')
        def on_status(data):
            print(f"\nUser status update: {data}")

        @self.sio.on('error')
        def on_error(data):
            print(f"\nError received: {data}")


    def connect_with_session(self, session_id="00000000-0000-0000-1111-000000000001"):
        """Connect to the WebSocket server with a known session ID"""
        try:
            self.session_id = session_id
            connection_url = f"{self.server_url}?sessionID={self.session_id}"
            print(f"Attempting to connect with URL: {connection_url}")

            self.sio.connect("http://127.0.0.1:5000", namespaces=['/'])
            print(f"Connected successfully with session ID: {self.session_id}")
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            raise

    def disconnect(self):
        if self.sio.connected:
            self.sio.disconnect()
            print("Disconnected from server")

    def stay_connected(self, duration=60):
        print(f"Keeping connection alive for {duration} seconds...")
        try:
            time.sleep(duration)
        except KeyboardInterrupt:
            print("\nStopping connection...")
        finally:
            self.disconnect()


if __name__ == "__main__":
    # Create tester instance
    tester = WebSocketTester()

    try:
        # Connect using the known session ID from dummy data
        tester.connect_with_session()

        # Try sending a message to user2
        tester.send_message(
            "00000000-0000-0000-0000-000000000002",  # USER_UUID2
            "Hello! This is a test message."
        )

        # Keep connection alive to see what happens
        tester.stay_connected(30)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        tester.disconnect()