import pytest
from flask import Blueprint

from src.app.extensions import db
from src.app.models.user import User
from datetime import datetime

from src.app.services.contact_service import ContactService
from src.app.services.message_service import MessageService
from src.app.services.user_service import UserService

###############################
### SETUP INTEGRATION TESTS
###############################
app = Blueprint('api', __name__)
user_service = UserService()
message_service = MessageService()
contact_service = ContactService()

# Testdaten
USERNAME = "testuser"
PASSWORD = "secure123"
USER_ID = "user-id-123"

USERNAME2 = "testuser2"
PASSWORD2 = "secure1234"
USER_ID2 = "user-id-456"


@pytest.fixture
def client(app):
    with app.test_client() as client:
        # Beispiel-Daten
        user = User(user_id=USER_ID, username=USERNAME, password=PASSWORD, salt="s", created_at=datetime.now())
        db.session.add(user)
        db.session.commit()
        yield client
        db.drop_all()


###############################
### SETUP INTEGRATION TESTS
###############################

# REGISTER
def test_register_success(client):
    res = client.post(f"/api/register?username={USERNAME2}&password={PASSWORD2}")
    print(res)
    assert res.status_code == 201


def test_register_duplicate(client):
    res = client.post(f"/api/register?username={USERNAME}&password={PASSWORD}")
    assert res.status_code == 409


# LOGIN
def test_login_success(client):
    res = client.get(f"/api/login?username={USERNAME}&password={PASSWORD}")
    assert res.status_code == 200


def test_login_invalid(client):
    res = client.get(f"/api/login?username=wrong&password=wrong")
    assert res.status_code == 401


# LOGOUT
def test_logout_success(mock_identity, mock_logout, client):
    mock_identity.return_value = USER_ID
    mock_logout.return_value = {}
    res = client.post("/api/logout")
    assert res.status_code == 200


def test_logout_fail(mock_identity, mock_logout, client):
    mock_identity.return_value = USER_ID
    mock_logout.return_value = {"error": "fail"}
    res = client.post("/api/logout")
    assert res.status_code == 500
