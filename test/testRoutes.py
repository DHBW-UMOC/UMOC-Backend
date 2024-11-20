import unittest
import requests

BASE_URL = "http://127.0.0.1:5001"  # Lokale URL der Flask-App


class TestEndpointsOnline(unittest.TestCase):
    def test_register_success(self):
        """Testet den /register-Endpunkt mit gültigen Daten."""
        response = requests.post(f"{BASE_URL}/register", data={
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 200)

    def test_register_missing_username(self):
        """Testet den /register-Endpunkt ohne Benutzernamen."""
        response = requests.post(f"{BASE_URL}/register", data={
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("No username provided for register", response.text)

    def test_login_success(self):
        """Testet den /login-Endpunkt mit gültigen Daten."""
        response = requests.get(f"{BASE_URL}/login", data={
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 200)

    def test_logout_missing_sessionID(self):
        """Testet den /logout-Endpunkt ohne sessionID."""
        response = requests.post(f"{BASE_URL}/logout", data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("No sessionID provided for logout", response.text)

    def test_add_contact_success(self):
        """Testet den /addContact-Endpunkt mit gültigen Daten."""
        response = requests.post(f"{BASE_URL}/addContact", data={
            'sessionID': '12345',
            'contact': 'testcontact'
        })
        self.assertEqual(response.status_code, 200)

    def test_change_contact_missing_status(self):
        """Testet den /changeContact-Endpunkt ohne Status."""
        response = requests.post(f"{BASE_URL}/changeContact", data={
            'sessionID': '12345',
            'contact': 'testcontact'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("No status provided for changeContact", response.text)

    def test_save_message_success(self):
        """Testet den /saveMessage-Endpunkt mit einer Nachricht."""
        response = requests.post(f"{BASE_URL}/saveMessage/", data={
            'message': 'Hello World'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("Message saved successfully", response.text)

    def test_get_messages(self):
        """Testet den /getMessages-Endpunkt."""
        response = requests.get(f"{BASE_URL}/getMessages")
        self.assertEqual(response.status_code, 200)

    def test_default_endpoint(self):
        """Testet den Standard-Endpunkt /."""
        response = requests.get(f"{BASE_URL}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Hello World", response.text)


if __name__ == "__main__":
    unittest.main()
