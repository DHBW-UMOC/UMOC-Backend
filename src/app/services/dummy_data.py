import uuid
from datetime import datetime
from app.extensions import db
from app.models.user import User, UserContact, ContactStatusEnum
from app.models.message import Message, MessageTypeEnum
from app.models.group import Group, GroupMember
from app.models.group import GroupRoleEnum


def insert_example_data():
    USER_UUID1 = "00000000-0000-0000-0000-000000000001"
    USER_UUID2 = "00000000-0000-0000-0000-000000000002"
    USER_UUID3 = "00000000-0000-0000-0000-000000000003"

    SESSION_UUID1 = "00000000-0000-0000-1111-000000000001"
    SESSION_UUID2 = "00000000-0000-0000-1111-000000000002"
    SESSION_UUID3 = "00000000-0000-0000-1111-000000000003"

    GROUP_NAME1 = "Group 1"
    GROUP_NAME2 = "Group 2"

    GROUP_UUID1 = "00000000-2222-0000-1111-000000000001"
    GROUP_UUID2 = "00000000-2222-0000-1111-000000000002"

    # Creating three users
    user1 = User(
        user_id=USER_UUID1,
        username="user1",
        password="password1",
        profile_picture="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png",
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
        profile_picture="https://avatars.githubusercontent.com/u/75573778?v=4",
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
        profile_picture="https://www.abgeordnetenwatch.de/sites/default/files/styles/opengraph_image/public/"
                        "politicians-profile-pictures/merkel_angela_chaperon_ci_110195_0.png",
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

    group1 = Group(
        group_id=GROUP_UUID1,
        group_name=GROUP_NAME1,
        admin_user_id=user1.user_id,
        created_at=datetime.now()
    )
    group2 = Group(
        group_id=GROUP_UUID2,
        group_name=GROUP_NAME2,
        admin_user_id=user2.user_id,
        created_at=datetime.now()
    )

    # Create GroupMember instances for the groups
    group_members = [
        GroupMember(
            group_id=GROUP_UUID1,
            user_id=user1.user_id,
            role=GroupRoleEnum.ADMIN,
            joined_at=datetime.now()
        ),
        GroupMember(
            group_id=GROUP_UUID1,
            user_id=user2.user_id,
            role=GroupRoleEnum.MEMBER,
            joined_at=datetime.now()
        ),
        GroupMember(
            group_id=GROUP_UUID1,
            user_id=user3.user_id,
            role=GroupRoleEnum.MEMBER,
            joined_at=datetime.now()
        )
    ]

    # Create Group instances
    group_messages = [
        Message(
            message_id=str(uuid.uuid4()),
            sender_user_id=user1.user_id,
            recipient_user_id=GROUP_UUID1,
            encrypted_content="Hello Group 1!",
            type=MessageTypeEnum.TEXT,
            send_at=datetime.now(),
            is_group=True
        ),
        Message(
            message_id=str(uuid.uuid4()),
            sender_user_id=GROUP_UUID2,
            recipient_user_id=GROUP_UUID2,
            encrypted_content="Hello Group 2!",
            type=MessageTypeEnum.TEXT,
            send_at=datetime.now(),
            is_group=True
        ),
        Message(
            message_id=str(uuid.uuid4()),
            sender_user_id=user3.user_id,
            recipient_user_id=GROUP_UUID1,
            encrypted_content="Hello Group 1 from Angela!",
            type=MessageTypeEnum.TEXT,
            send_at=datetime.now(),
            is_group=True
        ),
    ]

    # Add all to the session
    db.session.add_all([user1, user2, user3, user4, user5, user6])
    db.session.add_all(contacts)
    db.session.add_all(messages)
    db.session.add_all([group1, group2])
    db.session.add_all(group_members)
    db.session.add_all(group_messages)

    # Commit the session to save data
    db.session.commit()
    print("Example data inserted successfully.")
