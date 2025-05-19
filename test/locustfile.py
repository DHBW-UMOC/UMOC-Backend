from locust import HttpUser, task, between
import random
import string

real_contact_name = "Max Mustermann"
real_contact_id = "00000000-0000-0000-0000-000000000002"

def random_username():
    return "user_" + ''.join(random.choices(string.ascii_letters + string.digits, k=8))

class FlaskUser(HttpUser):
    wait_time = between(1, 1.5)

    def on_start(self):
        """Called when a simulated user starts. Registers and logs in."""
        self.username = random_username()
        self.password = "Test1234"
        self.register_user()
        self.login_user()

    def register_user(self):
        response = self.client.post("/register", json={
            "username": self.username,
            "password": self.password,
            "profile_pic": None
        })
        if response.status_code != 201:
            print("Failed to register user:", self.username)

    def login_user(self):
        response = self.client.get("/login", json={
            "username": self.username,
            "password": self.password
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            print(f"Login failed for user {self.username}: {response.status_code}")

    @task
    def add_contact(self):
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}

        # Register a new contact first
        contact_name = random_username()
        self.client.post("/register", json={
            "username": contact_name,
            "password": "Test1234"
        })

        # Then add the contact
        self.client.post("/addContact", json={
            "contact_name": contact_name
        }, headers=headers)

    @task
    def get_chats(self):
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/getChats", headers=headers)
        if response.status_code != 200:
            print("Failed to get chats:", response.status_code)

    @task
    def get_all_users(self):
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/getAllUsers", json={"searchBy": "user"}, headers=headers)
        if response.status_code != 200:
            print("Failed to get all users:", response.status_code)

    @task
    def save_message(self):
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.post("/saveMessage", json={
            "recipient_id": real_contact_id,
            "content": "Hello, this is a test message!"
        }, headers=headers)
        if response.status_code != 200:
            print("Failed to save message:", response.status_code)