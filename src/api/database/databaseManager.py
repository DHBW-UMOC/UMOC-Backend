from flask import Flask

from src.api.database.models import Message, db, _MESSAGE


def init_db(app: Flask):
    db.init_app(app)
    with app.app_context():
        db.create_all()


def saveMessage(message: str):
    _Message = _MESSAGE(message=message)
    db.session.add(_Message)
    db.session.commit()


def getMessages():
    return Message.query.all()
