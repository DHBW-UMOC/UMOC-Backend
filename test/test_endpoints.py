import unittest
from unittest.mock import patch
import requests

BASE_URL = "http://127.0.0.1:5000"


class TestEndpoints(unittest.TestCase):

    @patch("requests.post")
    def test_register_success(self, mock_post):
        """Tests the /register endpoint with valid data."""
        mock_post.return_value.status_code = 200
        response = requests.post(f"{BASE_URL}/register", data={
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 200)

    @patch("requests.post")
    def test_register_missing_username(self, mock_post):
        """Tests the /register endpoint without a username."""
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "No username provided for register"
        response = requests.post(f"{BASE_URL}/register", data={
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("No username provided for register", response.text)

    @patch("requests.post")
    def test_save_message_success(self, mock_post):
        """Tests the /saveMessage endpoint with a valid message."""
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = "Message saved successfully"
        response = requests.post(f"{BASE_URL}/saveMessage", data={
            'message': 'Hello World'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("Message saved successfully", response.text)

    @patch("requests.get")
    def test_get_messages(self, mock_get):
        """Tests the /getMessages endpoint."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{"message": "Hello World"}]
        response = requests.get(f"{BASE_URL}/getMessages")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{"message": "Hello World"}])


if __name__ == "__main__":
    unittest.main()