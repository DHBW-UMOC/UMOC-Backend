from flask import Blueprint, request, jsonify

from src.api.database import databaseManager

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


@endpointApp.route("/saveMessage/", methods=["POST"])
def saveMessage():
    message = request.form.get('message')

    if not message:
        return jsonify({"error": "No message provided"}), 400
    databaseManager.saveMessage(message)
    return jsonify({"message": "Message saved successfully"}), 200



@endpointApp.route("/getMessages")
def getMessage():
    return databaseManager.getMessages()
