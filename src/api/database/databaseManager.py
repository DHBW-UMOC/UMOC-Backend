import datetime
import uuid

from api.database.models import Message
from api.database.models import MessageTypeEnum
from api.database.models import db, User, UserContact, ContactStatusEnum
from flask import Flask, jsonify


def init_db(app: Flask):
    db.init_app(app)
    with app.app_context():
        db.create_all()


def reset_database(app):
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        print("Database reset completed.")

##########################
## DATABASE ACCESS FUNCTIONS
##########################
def addUser(username: str, password: str, public_key: str): #TODO add actual numbers
    _User = User(username=username, password=password, public_key=public_key, salt="", created_at=datetime.date.today())
    db.session.add(_User)
    db.session.commit()


def setSessionId(username: str, password: str, sessionID: uuid):
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        user.session_id = sessionID
        db.session.commit()
        return True
    else:
        return False


def resetSessionId(sessionID: uuid):
    user = User.query.filter_by(session_id=sessionID).first()
    if user:
        user.session_id = None
        db.session.commit()
        return True
    else:
        return False


def addContact(sessionID: uuid, contact: str):
    user = User.query.filter_by(session_id=sessionID).first()

    if user:
        userContact = UserContact(user_id=user.user_id, contact_id=contact)
        db.session.add(userContact)
        db.session.commit()
        return True
    else:
        return False


def changeContact(sessionID: uuid, contact: str, status: ContactStatusEnum):
    user = User.query.filter_by(session_id=sessionID).first()
    userContact = UserContact.query.filter_by(user_id=user.user_id, contact_id=contact).first()

    if user and userContact:
        userContact.status = status
        db.session.commit()
        return True
    else:
        return False


def getContacts(sessionID: uuid):
    user = User.query.filter_by(session_id=sessionID).first()
    if not user:
        return jsonify({"error": "User not found. SessionID is wrong...Probably"})

    userContacts = UserContact.query.filter_by(user_id=user.user_id)

    contact_list = [
        {"contact_id": contact.contact_id,
         "name": User.query.filter_by(user_id=contact.contact_id).first().username,
         "url": "https://static.spektrum.de/fm/912/f2000/205090.jpg"}
        for contact in userContacts
    ]

    return jsonify(contact_list)


def getContactMessages(sessionID: uuid, contactID: uuid):
    user = User.query.filter_by(session_id=sessionID).first()

    if not user:
        return jsonify({"error": "User not found. SessionID is wrong"})
    userContact = UserContact.query.filter_by(user_id=user.user_id, contact_id=contactID).first()

    if not userContact:
        return jsonify({"error": "Contact not found"})
    messages = Message.query.filter_by(sender_user_id=user.user_id, recipient_user_id=userContact.contact_id).all()

    messages_list = [{"content": message.encrypted_content, "sender_user_id": message.sender_user_id, "send_at": message.send_at} for message in messages]

    return jsonify(messages_list)


##########################
## TEST DATABASE FUNCTIONS
##########################
def saveMessage(sessionID: uuid, recipientID: uuid, content: str, isGroup: bool=False, messageType: MessageTypeEnum=MessageTypeEnum.TEXT):
    userID = User.query.filter_by(session_id=sessionID).first().user_id

    if not userID:
        return jsonify({"error": "User not found. SessionID is wrong."})

    message = Message(
        sender_user_id=userID,
        recipient_user_id=recipientID,
        encrypted_content=content,
        type=messageType,
        send_at=datetime.datetime.now(),
        is_group=isGroup
    )
    db.session.add(message)
    db.session.commit()

    return jsonify({"message": "Message saved successfully"}), 200

