import uuid
from datetime import datetime

from api.database.models import User, UserContact, Message, ContactStatusEnum, MessageTypeEnum
from api.database.models import db


def insert_example_data():
    # Creating three users
    user1 = User(
        user_id=str(uuid.uuid4()),
        username="user1",
        password="password1",
        salt="salt1",
        created_at=datetime.now(),
        session_id=str(uuid.uuid4()),
        public_key="public_key_user1",
        encrypted_private_key="encrypted_private_key_user1",
        is_online=True
    )

    user2 = User(
        user_id=str(uuid.uuid4()),
        username="user2",
        password="password2",
        salt="salt2",
        created_at=datetime.now(),
        session_id=str(uuid.uuid4()),
        public_key="public_key_user2",
        encrypted_private_key="encrypted_private_key_user2",
        is_online=False
    )

    user3 = User(
        user_id=str(uuid.uuid4()),
        username="user3",
        password="password3",
        salt="salt3",
        created_at=datetime.now(),
        session_id=str(uuid.uuid4()),
        public_key="public_key_user3",
        encrypted_private_key="encrypted_private_key_user3",
        is_online=True
    )

    # Adding contacts for user1
    contact1 = UserContact(
        user_id=user1.user_id,
        contact_id=user2.user_id,
        status=ContactStatusEnum.FRIEND,
        time_out=None,
        streak=0,
        continue_streak=True
    )

    contact2 = UserContact(
        user_id=user1.user_id,
        contact_id=user3.user_id,
        status=ContactStatusEnum.NEW,
        time_out=None,
        streak=0,
        continue_streak=True
    )

    # Adding contacts for user2
    contact3 = UserContact(
        user_id=user2.user_id,
        contact_id=user1.user_id,
        status=ContactStatusEnum.FRIEND,
        time_out=None,
        streak=1,
        continue_streak=True
    )

    contact4 = UserContact(
        user_id=user2.user_id,
        contact_id=user3.user_id,
        status=ContactStatusEnum.BLOCKED,
        time_out=None,
        streak=0,
        continue_streak=False
    )

    # Adding a sample message
    message1 = Message(
        message_id=str(uuid.uuid4()),
        sender_user_id=user1.user_id,
        recipient_user_id=user2.user_id,
        encrypted_content="Hello, this is a test message.",
        type=MessageTypeEnum.TEXT,
        send_at=datetime.now(),
        updated_at=datetime.now(),
        is_group=False
    )

    # Add all to the session
    db.session.add_all([user1, user2, user3, contact1, contact2, contact3, contact4, message1])

    # Commit the session to save data
    db.session.commit()
    print("Example data inserted successfully.")
