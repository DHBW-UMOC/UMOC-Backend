from locust import HttpUser, task, between
import random
import string

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

        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        fake_contact_name = random_username()
        self.client.post("/addContact", json={
            "contact_name": fake_contact_name
        }, headers=headers)