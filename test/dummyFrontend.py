import requests

# Base URL for your Flask API
BASE_URL = "http://localhost:5000"

# Authorization token (replace 'secure_token_here' with your actual token)
AUTH_TOKEN = "secure_token_here"

# Headers for authorization
HEADERS = {
    "Authorization": AUTH_TOKEN,
    "Content-Type": "application/json"
}

def login(username):
    """Simulates logging in by sending a username to the /login endpoint."""
    response = requests.post(f"{BASE_URL}/login", data={"username": username})
    if response.status_code == 200:
        print("Logged in successfully.")
    else:
        print("Login failed:", response.text)

def save_message(message):
    """Sends a message to the /saveMessage endpoint."""
    payload = {"message": message}
    response = requests.post(f"{BASE_URL}/saveMessage", json=payload, headers=HEADERS)
    if response.status_code == 200:
        print("Message saved successfully:", response.json())
    else:
        print("Failed to save message:", response.text)

def get_messages():
    """Retrieves messages from the /getMessages endpoint."""
    response = requests.get(f"{BASE_URL}/getMessages", headers=HEADERS)
    if response.status_code == 200:
        messages = response.json()
        print("Retrieved messages:", messages)
    else:
        print("Failed to retrieve messages:", response.text)

# Test the API functions
if __name__ == "__main__":
    username = "test_user"  # Replace with your test username
    message = "Hello from the test script!"  # Replace with your test message

    print("Testing login...")
    login(username)

    print("\nTesting saveMessage...")
    save_message(message)

    print("\nTesting getMessages...")
    get_messages()
