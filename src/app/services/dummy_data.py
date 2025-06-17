import uuid
from datetime import datetime
from app import db
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
    GROUP_NAME3 = "TINF23B4"

    GROUP_UUID1 = "00000000-2222-0000-1111-000000000001"
    GROUP_UUID2 = "00000000-2222-0000-1111-000000000002"
    GROUP_UUID3 = "00000000-2222-0000-1111-000000000003"

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
        is_online=True,
        points=20
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
        is_online=False,
        points=20
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
        is_online=True,
        points=20
    )

    # Adding more users (simplified)
    user4 = User(user_id="00000000-0000-0000-0000-000000000004", username="Günter", 
                 password="password4", salt="salt4", created_at=datetime.now(),
                 session_id="00000000-0000-0000-1111-000000000004", points=20)
    
    user5 = User(user_id="00000000-0000-0000-0000-000000000005", username="Trump", 
                 password="password5", salt="salt5", created_at=datetime.now(),
                 session_id="00000000-0000-0000-1111-000000000005", points=20)
    
    user6 = User(user_id="00000000-0000-0000-0000-000000000006", username="Lucas", 
                 password="password6", salt="salt6", created_at=datetime.now(),
                 session_id="00000000-0000-0000-1111-000000000006", points=20)
    

    
    user7 = User(user_id="00000000-0000-0000-0000-000000000007", username="Omar", 
                 password="123456789", salt="salt7", created_at=datetime.now(),
                 session_id="00000000-0000-0000-1111-000000000007", points=20)
    user8 = User(user_id="00000000-0000-0000-0000-000000000008", username="Adrian", 
                 password="123456789", salt="salt8", created_at=datetime.now(),
                 session_id="00000000-0000-0000-1111-000000000008", points=20)
    user9 = User(user_id="00000000-0000-0000-0000-000000000009", username="Carina", 
                 password="123456789", salt="salt9", created_at=datetime.now(),
                 session_id="00000000-0000-0000-1111-000000000009", points=20)
    user10 = User(user_id="00000000-0000-0000-0000-000000000010", username="Cedric", 
                  password="123456789", salt="salt10", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000010", points=20)
    user11 = User(user_id="00000000-0000-0000-0000-000000000011", username="Chris", 
                  password="123456789", salt="salt11", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000011", points=20)
    user12 = User(user_id="00000000-0000-0000-0000-000000000012", username="Christoph", 
                  password="123456789", salt="salt12", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000012", points=20)
    user13 = User(user_id="00000000-0000-0000-0000-000000000013", username="Don", 
                  password="123456789", salt="salt13", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000013", points=20)
    user14 = User(user_id="00000000-0000-0000-0000-000000000014", username="Hannah", 
                  password="123456789", salt="salt14", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000014", points=20)
    user15 = User(user_id="00000000-0000-0000-0000-000000000015", username="Jan T", 
                  password="123456789", salt="salt15", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000015", points=20)
    user16 = User(user_id="00000000-0000-0000-0000-000000000016", username="Jan B", 
                  password="123456789", salt="salt16", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000016", points=20)
    user17 = User(user_id="00000000-0000-0000-0000-000000000017", username="Julian", 
                  password="123456789", salt="salt17", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000017", points=20)
    user18 = User(user_id="00000000-0000-0000-0000-000000000018", username="Michi", 
                  password="123456789", salt="salt18", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000018", points=20)
    user19 = User(user_id="00000000-0000-0000-0000-000000000019", username="Leo", 
                  password="123456789", salt="salt19", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000019", points=20)
    user20 = User(user_id="00000000-0000-0000-0000-000000000020", username="Leon", 
                  password="123456789", salt="salt20", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000020", points=20)
    user21 = User(user_id="00000000-0000-0000-0000-000000000021", username="Lukas", 
                  password="123456789", salt="salt21", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000021", points=20)
    user22 = User(user_id="00000000-0000-0000-0000-000000000022", username="Marcel", 
                  password="123456789", salt="salt22", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000022", points=20)
    user23 = User(user_id="00000000-0000-0000-0000-000000000023", username="Nico", 
                  password="123456789", salt="salt23", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000023", points=20)
    user24 = User(user_id="00000000-0000-0000-0000-000000000024", username="Orlando Legolas", 
                  password="123456789", salt="salt24", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000024", points=20)
    user25 = User(user_id="00000000-0000-0000-0000-000000000025", username="Oaskar", 
                  password="123456789", salt="salt25", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000025", points=20)
    user26 = User(user_id="00000000-0000-0000-0000-000000000026", username="Patric", 
                  password="123456789", salt="salt26", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000026", points=20)
    user27 = User(user_id="00000000-0000-0000-0000-000000000027", username="Sid", 
                  password="123456789", salt="salt27", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000027", points=20)
    user28 = User(user_id="00000000-0000-0000-0000-000000000028", username="Tim", 
                  password="123456789", salt="salt28", created_at=datetime.now(),
                  session_id="00000000-0000-0000-1111-000000000028", points=20)

    # Create a new admin user
    admin_user = User(
        user_id="00000000-0000-0000-0000-000000000029",
        username="admin",
        password="umoc123456789",
        salt="salt29",
        created_at=datetime.now(),
        session_id="00000000-0000-0000-1111-000000000029",
        points=1000
    )

    # Add the admin user to the group with admin privileges
    admin_group_member = GroupMember(
        group_id=GROUP_UUID3,
        user_id=admin_user.user_id,
        role=GroupRoleEnum.ADMIN,
        joined_at=datetime.now()
    )

    # Adding contacts for users
    contacts = [
        UserContact(user_id=user1.user_id, contact_id=user2.user_id, status=ContactStatusEnum.FRIEND),
        UserContact(user_id=user1.user_id, contact_id=user3.user_id, status=ContactStatusEnum.NEW),
        UserContact(user_id=user2.user_id, contact_id=user1.user_id, status=ContactStatusEnum.FRIEND),
        UserContact(user_id=user2.user_id, contact_id=user3.user_id, status=ContactStatusEnum.BLOCK),
        UserContact(user_id=user1.user_id, contact_id=user4.user_id, status=ContactStatusEnum.NEW),
        UserContact(user_id=user1.user_id, contact_id=user6.user_id, status=ContactStatusEnum.NEW),
        UserContact(user_id=user2.user_id, contact_id=user4.user_id, status=ContactStatusEnum.NEW),
        UserContact(user_id=user2.user_id, contact_id=user5.user_id, status=ContactStatusEnum.NEW)
    ]

    # Adding some sample messages
    # messages = [
    #     Message(
    #         message_id=str(uuid.uuid4()),
    #         sender_user_id=user1.user_id,
    #         recipient_user_id=user2.user_id,
    #         encrypted_content="Hello, this is a test message.",
    #         type=MessageTypeEnum.TEXT,
    #         send_at=datetime.now(),
    #         is_group=False
    #     ),
    #     Message(
    #         message_id=str(uuid.uuid4()),
    #         sender_user_id=user1.user_id,
    #         recipient_user_id=user2.user_id,
    #         encrypted_content="This is another test message with longer text.",
    #         type=MessageTypeEnum.TEXT,
    #         send_at=datetime.now(),
    #         is_group=False
    #     ),
    #     Message(
    #         message_id=str(uuid.uuid4()),
    #         sender_user_id=user2.user_id,
    #         recipient_user_id=user1.user_id,
    #         encrypted_content="I am user2 and I respond.",
    #         type=MessageTypeEnum.TEXT,
    #         send_at=datetime.now(),
    #         is_group=False
    #     )
    # ]

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
    group3 = Group(
        group_id=GROUP_UUID3,
        group_name=GROUP_NAME3,
        admin_user_id=user7.user_id,  # Assign user7 as the admin
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

    # Add users 7-28 to the new group
    group3_members = [
        GroupMember(
            group_id=GROUP_UUID3,
            user_id=user.user_id,
            role=GroupRoleEnum.MEMBER,
            joined_at=datetime.now()
        )
        for user in [user7, user8, user9, user10, user11, user12, user13, user14, user15, user16, user17, user18, user19, user20, user21, user22, user23, user24, user25, user26, user27, user28]
    ]

    # Create a separate admin_group_member for the admin user
    admin_group_member = GroupMember(
        group_id=GROUP_UUID3,
        user_id=admin_user.user_id,
        role=GroupRoleEnum.ADMIN,
        joined_at=datetime.now()
    )

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
    db.session.add_all([
        user7, user8, user9, user10, user11, user12, user13, user14, user15, user16, user17, user18, user19, user20, user21, user22, user23, user24, user25, user26, user27, user28, admin_user
    ])
    db.session.add_all(contacts)
    #db.session.add_all(messages)
    db.session.add_all([group1, group2, group3])
    db.session.add_all(group_members)
    db.session.add_all(group_messages)
    db.session.add_all(group3_members)
    db.session.add(admin_group_member)

    # Commit the session to save data
    db.session.commit()
    print("Example data inserted successfully.")
    db.session.add_all([user1, user2, user3, user4, user5, user6])
    db.session.add_all([
        user7, user8, user9, user10, user11, user12, user13, user14, user15, user16, user17, user18, user19, user20, user21, user22, user23, user24, user25, user26, user27, user28, admin_user
    ])
    db.session.add_all(contacts)
    #db.session.add_all(messages)
    db.session.add_all([group1, group2, group3])
    db.session.add_all(group_members)
    db.session.add_all(group_messages)
    db.session.add_all(group3_members)
    db.session.add(admin_user)
    db.session.add(admin_group_member)

    # Commit the session to save data
    db.session.commit()
    print("Example data inserted successfully.")
