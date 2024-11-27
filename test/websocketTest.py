import websocket
import json

# Replace with the actual WebSocket server URL
SERVER_URL = "ws://localhost:5000"


def on_message(ws, message):
    print(f"Received: {message}")


def on_error(ws, error):
    print(f"Error: {error}")


def on_close(ws, close_status_code, close_msg):
    print("Connection closed")


def on_open(ws):
    print("Connection opened")
    # Example: Connect endpoint
    session_id = "00000000-0000-0000-1111-000000000001"  # Replace with a valid session ID
    ws.send(json.dumps({"sessionID": session_id}))

    # Example: Send a message
    ws.send(json.dumps({
        "sessionID": session_id,
        "recipient_id": 2,  # Replace with valid recipient ID
        "content": "Hello, WebSocket!",
        "is_group": False,
        "type": "text"
    }))


if __name__ == "__main__":
    ws = websocket.connect(f"{SERVER_URL}/socket.io/",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
