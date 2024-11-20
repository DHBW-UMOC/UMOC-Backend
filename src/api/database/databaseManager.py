import uuid

from flask import Flask, jsonify
import datetime

from api.database.models import db, Message, User, UserContact, ContactStatusEnum

from api.database.models import Message


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
    else:
        return False


def resetSessionId(sessionID: uuid):
    user = User.query.filter_by(session_id=sessionID).first()
    if user:
        user.session_id = None
        db.session.commit()
    else:
        return False


def addContact(sessionID: uuid, contact: str):
    user = User.query.filter_by(session_id=sessionID).first()

    if user:
        userContact = UserContact(user_id=user.user_id, contact_id=contact)
        db.session.add(userContact)
        db.session.commit()
    else:
        return False


def changeContact(sessionID: uuid, contact: str, status: ContactStatusEnum):
    user = User.query.filter_by(session_id=sessionID).first()
    userContact = UserContact.query.filter_by(user_id=user.user_id, contact_id=contact).first()

    if user and userContact:
        userContact.status = status
        db.session.commit()
    else:
        return False


def getContacts(sessionID: uuid):
    user = User.query.filter_by(session_id=sessionID).first()
    userContacts = UserContact.query.filter_by(user_id=user.user_id)

    contact_list = [{"contact_id": contact.contact_id, "name": "Bla", "url": "https://static.spektrum.de/fm/912/f2000/205090.jpg"} for contact in userContacts]

    return jsonify({"contacts": contact_list})


def getContactMessages(sessionID: uuid, contact: str):
    user = User.query.filter_by(session_id=sessionID).first()
    userContact = UserContact.query.filter_by(user_id=user.user_id, contact_id=contact).first()
    messages = Message.query.filter_by(sender_user_id=user.user_id, recipient_user_id=userContact.contact_id).all()

    messages_list = [{"content": message.encrypted_content, "sender_user_id": message.sender_user_id, "send_at": message.send_at} for message in messages]

    return jsonify({"messages": messages_list})


##########################
## TEST DATABASE FUNCTIONS
##########################
def saveMessage(message: str, sender_id, content, timestamp, group, recipient_id, message_type):
    _Message = Message(message, message_id=uuid.uuid4, sender_user_id=sender_id, recipient_user_id=recipient_id, encrypted_content=content, type=message_type, send_at=timestamp, is_group=group)
    db.session.add(_Message)
    db.session.commit()


def getMessages():
    return _MESSAGE.query.all()
