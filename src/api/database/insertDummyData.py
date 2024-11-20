import uuid
from datetime import datetime

from api.database.models import User, UserContact, Message, ContactStatusEnum, MessageTypeEnum
from api.database.models import db


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
        username="user2",
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
        username="Bernd",
        password="password3",
        salt="salt3",
        created_at=datetime.now(),
        session_id=SESSION_UUID3,
        public_key="public_key_user3",
        encrypted_private_key="encrypted_private_key_user3",
        is_online=True
    )

    user4 = User(
        user_id="00000000-0000-0000-0000-000000000004",
        username="Günter",
        password="password4",
        salt="salt4",
        created_at=datetime.now(),
        session_id="00000000-0000-0000-1111-000000000004",
        public_key="public_key_user4",
        encrypted_private_key="encrypted_private_key_user4",
        is_online=True
    )

    user5 = User(
        user_id="00000000-0000-0000-0000-000000000005",
        username="Nick",
        password="password5",
        salt="salt5",
        created_at=datetime.now(),
        session_id="00000000-0000-0000-1111-000000000005",
        public_key="public_key_user5",
        encrypted_private_key="encrypted_private_key_user5",
        is_online=True
    )

    user6 = User(
        user_id="00000000-0000-0000-0000-000000000006",
        username="Pascal",
        password="password6",
        salt="salt6",
        created_at=datetime.now(),
        session_id="00000000-0000-0000-1111-000000000006",
        public_key="public_key_user6",
        encrypted_private_key="encrypted_private_key_user6",
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

    contact5 = UserContact(
        user_id=user1.user_id,
        contact_id=user4.user_id,
        status=ContactStatusEnum.NEW,
        time_out=None,
        streak=0,
        continue_streak=True
    )

    contact6 = UserContact(
        user_id=user1.user_id,
        contact_id=user5.user_id,
        status=ContactStatusEnum.NEW,
        time_out=None,
        streak=0,
        continue_streak=True
    )

    contact7 = UserContact(
        user_id=user1.user_id,
        contact_id=user6.user_id,
        status=ContactStatusEnum.NEW,
        time_out=None,
        streak=0,
        continue_streak=True
    )

    contact8 = UserContact(
        user_id=user2.user_id,
        contact_id=user4.user_id,
        status=ContactStatusEnum.NEW,
        time_out=None,
        streak=0,
        continue_streak=True
    )

    contact9 = UserContact(
        user_id=user2.user_id,
        contact_id=user5.user_id,
        status=ContactStatusEnum.NEW,
        time_out=None,
        streak=0,
        continue_streak=True
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

    message2 = Message(
        message_id=str(uuid.uuid4()),
        sender_user_id=user1.user_id,
        recipient_user_id=user2.user_id,
        encrypted_content="This is another test message. This time with a longer text. A very long text. A very very long text. A very very very long text. A very very very very long text. A very very very very very long text. A very very very very very very long text. A very very very very very very very long text. A very very very very very very very very long text. A very very very very very very very very very long text. A",
        type=MessageTypeEnum.TEXT,
        send_at=datetime.now(),
        updated_at=datetime.now(),
        is_group=False
    )

    message3 = Message(
        message_id=str(uuid.uuid4()),
        sender_user_id=user2.user_id,
        recipient_user_id=user1.user_id,
        encrypted_content="I am user2. and i responde.",
        type=MessageTypeEnum.TEXT,
        send_at=datetime.now(),
        updated_at=datetime.now(),
        is_group=False
    )

    message4 = Message(
        message_id=str(uuid.uuid4()),
        sender_user_id=user1.user_id,
        recipient_user_id=user3.user_id,
        encrypted_content="This is a test message. This time with a longer text. A very long text. A very very long text. A very very very long text. A very very very very long text. A very very very very very long text. A very very very very very very long text. Test message.",
        type=MessageTypeEnum.TEXT,
        send_at=datetime.now(),
        updated_at=datetime.now(),
        is_group=False
    )

    message5 = Message(
        message_id=str(uuid.uuid4()),
        sender_user_id=user1.user_id,
        recipient_user_id=user2.user_id,
        encrypted_content="I dont know what to say. im user 1 and you are user 2.",
        type=MessageTypeEnum.TEXT,
        send_at=datetime.now(),
        updated_at=datetime.now(),
        is_group=False
    )

    message6 = Message(
        message_id=str(uuid.uuid4()),
        sender_user_id=user1.user_id,
        recipient_user_id=user4.user_id,
        encrypted_content="Chat between user1 and user4. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet",
        type=MessageTypeEnum.TEXT,
        send_at=datetime.now(),
        updated_at=datetime.now(),
        is_group=False
    )

    message7 = Message(
        message_id=str(uuid.uuid4()),
        sender_user_id=user1.user_id,
        recipient_user_id=user5.user_id,
        encrypted_content="Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
        type=MessageTypeEnum.TEXT,
        send_at=datetime.now(),
        updated_at=datetime.now(),
        is_group=False
    )

    message8 = Message(
        message_id=str(uuid.uuid4()),
        sender_user_id=user1.user_id,
        recipient_user_id=user6.user_id,
        encrypted_content="Chat between user1 and user6. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet",
        type=MessageTypeEnum.TEXT,
        send_at=datetime.now(),
        updated_at=datetime.now(),
        is_group=False
    )

    message9 = Message(
        message_id=str(uuid.uuid4()),
        sender_user_id=user2.user_id,
        recipient_user_id=user4.user_id,
        encrypted_content="Chat between user2 and user4. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet",
        type=MessageTypeEnum.TEXT,
        send_at=datetime.now(),
        updated_at=datetime.now(),
        is_group=False
    )

    message10 = Message(
        message_id=str(uuid.uuid4()),
        sender_user_id=user1.user_id,
        recipient_user_id=user2.user_id,
        encrypted_content="Chat between user1 and user2. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet",
        type=MessageTypeEnum.TEXT,
        send_at=datetime.now(),
        updated_at=datetime.now(),
        is_group=False
    )

    message11 = Message(
        message_id=str(uuid.uuid4()),
        sender_user_id=user2.user_id,
        recipient_user_id=user1.user_id,
        encrypted_content="Chat between user2 and user1. Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet",
        type=MessageTypeEnum.TEXT,
        send_at=datetime.now(),
        updated_at=datetime.now(),
        is_group=False
    )

    message12 = Message(
        message_id=str(uuid.uuid4()),
        sender_user_id=user1.user_id,
        recipient_user_id=user2.user_id,
        encrypted_content="Generiere einfach soviel Lorem Ipsum Text wie du brauchst. Kopiere und füge ihn in dein Layout als vorübergehenden Platzhalter ein und schon sieht das Projekt ein Stückchen vollständiger aus. Viel Spaß dabei.",
        type=MessageTypeEnum.TEXT,
        send_at=datetime.now(),
        updated_at=datetime.now(),
        is_group=False
    )

    message13 = Message(
        message_id=str(uuid.uuid4()),
        sender_user_id=user1.user_id,
        recipient_user_id=user2.user_id,
        encrypted_content="Hier können verschieden Varianten von Lorem ipsum Text heruntergeladen werden. Jedes Beispiel ist als reines Text- oder Worddokument (in .zip Format) verfügbar. PC - per Klick auf die rechte Maustaste und dann speichern. Mac -Taste gedrückt halten und klicken, Dokument wird automatisch auf den Schreibtisch gespeichert.",
        type=MessageTypeEnum.TEXT,
        send_at=datetime.now(),
        updated_at=datetime.now(),
        is_group=False
    )

    message14 = Message(
        message_id=str(uuid.uuid4()),
        sender_user_id=user2.user_id,
        recipient_user_id=user1.user_id,
        encrypted_content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam nec purus ac libero ultricies tristique",
        type=MessageTypeEnum.TEXT,
        send_at=datetime.now(),
        updated_at=datetime.now(),
        is_group=False
    )



    # Add all to the session
    db.session.add_all([user1, user2, user3, user4, user5, user6, contact1, contact2, contact3, contact4, contact5, contact6, contact7, contact8, contact9, message1, message2, message3, message4, message5, message6, message7, message8, message9, message10, message11, message12, message13, message14])

    # Commit the session to save data
    db.session.commit()
    print("Example data inserted successfully.")
