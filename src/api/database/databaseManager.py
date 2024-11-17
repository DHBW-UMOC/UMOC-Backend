import uuid

from flask import Flask
import datetime

from api.database.models import db, _MESSAGE, User, UserContact, ContactStatusEnum


def init_db(app: Flask):
    db.init_app(app)
    with app.app_context():
        db.create_all()


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


##########################
## TEST DATABASE FUNCTIONS
##########################
def saveMessage(message: str):
    _Message = _MESSAGE(message=message)
    db.session.add(_Message)
    db.session.commit()


def getMessages():
    return _MESSAGE.query.all()
