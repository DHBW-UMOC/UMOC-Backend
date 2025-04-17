import uuid
from datetime import datetime
from src.app.extensions import db
from src.app.models.user import User, UserContact, ContactStatusEnum
from src.app.models.message import Message, MessageTypeEnum

def insert_example_data():
    USER_UUID1 = "00000000-0000-0000-0000-000000000001"
    USER_UUID2 = "00000000-0000-0000-0000-000000000002"
    USER_UUID3 = "00000000-0000-0000-0000-000000000003"

    SESSION_UUID1 = "00000000-0000-0000-1111-000000000001"
    SESSION_UUID2 = "00000000-0000-0000-1111-000000000002"
    SESSION_UUID3 = "00000000-0000-0000-1111-000000000003"

    # Creating three users
    user1 = User(
        user_id=USER_UUID1,
        username="user1",
        password="password1",
        salt="salt1",
        created_at=datetime.now(),
        session_id=SESSION_UUID1,
        public_key="public_key_user1",
        encrypted_private_key="encrypted_private_key_user1",
        is_online=True
    )

    user2 = User(
        user_id=USER_UUID2,
        username="Max Mustermann",
        password="password2",
        salt="salt2",
        created_at=datetime.now(),
        session_id=SESSION_UUID2,
        public_key="public_key_user2",
        encrypted_private_key="encrypted_private_key_user2",
        is_online=False
    )

    user3 = User(
        user_id=USER_UUID3,
        username="Angela Merkel",
        password="password3",
        salt="salt3",
        created_at=datetime.now(),
        session_id=SESSION_UUID3,
        public_key="public_key_user3",
        encrypted_private_key="encrypted_private_key_user3",
        is_online=True
    )

    # Adding more users (simplified)
    user4 = User(user_id="00000000-0000-0000-0000-000000000004", username="Günter", 
                 password="password4", salt="salt4", created_at=datetime.now(),
                 session_id="00000000-0000-0000-1111-000000000004")
    
    user5 = User(user_id="00000000-0000-0000-0000-000000000005", username="Trump", 
                 password="password5", salt="salt5", created_at=datetime.now(),
                 session_id="00000000-0000-0000-1111-000000000005")
    
    user6 = User(user_id="00000000-0000-0000-0000-000000000006", username="Lucas", 
                 password="password6", salt="salt6", created_at=datetime.now(),
                 session_id="00000000-0000-0000-1111-000000000006")

    # Adding contacts for users
    contacts = [
        UserContact(user_id=user1.user_id, contact_id=user2.user_id, status=ContactStatusEnum.FRIEND),
        UserContact(user_id=user1.user_id, contact_id=user3.user_id, status=ContactStatusEnum.NEW),
        UserContact(user_id=user2.user_id, contact_id=user1.user_id, status=ContactStatusEnum.FRIEND),
        UserContact(user_id=user2.user_id, contact_id=user3.user_id, status=ContactStatusEnum.BLOCKED),
        UserContact(user_id=user1.user_id, contact_id=user4.user_id, status=ContactStatusEnum.NEW),
        UserContact(user_id=user1.user_id, contact_id=user6.user_id, status=ContactStatusEnum.NEW),
        UserContact(user_id=user2.user_id, contact_id=user4.user_id, status=ContactStatusEnum.NEW),
        UserContact(user_id=user2.user_id, contact_id=user5.user_id, status=ContactStatusEnum.NEW)
    ]

    # Adding some sample messages
    messages = [
        Message(
            message_id=str(uuid.uuid4()),
            sender_user_id=user1.user_id,
            recipient_user_id=user2.user_id,
            encrypted_content="Hello, this is a test message.",
            type=MessageTypeEnum.TEXT,
            send_at=datetime.now(),
            is_group=False
        ),
        Message(
            message_id=str(uuid.uuid4()),
            sender_user_id=user1.user_id,
            recipient_user_id=user2.user_id,
            encrypted_content="This is another test message with longer text.",
            type=MessageTypeEnum.TEXT,
            send_at=datetime.now(),
            is_group=False
        ),
        Message(
            message_id=str(uuid.uuid4()),
            sender_user_id=user2.user_id,
            recipient_user_id=user1.user_id,
            encrypted_content="I am user2 and I respond.",
            type=MessageTypeEnum.TEXT,
            send_at=datetime.now(),
            is_group=False
        )
    ]

    # Add all to the session
    db.session.add_all([user1, user2, user3, user4, user5, user6])
    db.session.add_all(contacts)
    db.session.add_all(messages)

    # Commit the session to save data
    db.session.commit()
    print("Example data inserted successfully.")
