from .database import databaseManager
from .database.models import User, Group
from flask import Blueprint, Flask, jsonify, request
from .database import databaseManager

endpointApp = Blueprint('main', __name__)


###########################
## REST-API ENDPOINTS
##########################

@endpointApp.route("/")
def default():
    return "Hello World"

@endpointApp.route("/login", methods=['GET', 'POST'])
def login():
    "This is login"


@endpointApp.route("/saveMessage", methods=["POST"])
def saveMessage():
    pass

@endpointApp.route("/getMessages")
def getMessage():
    pass