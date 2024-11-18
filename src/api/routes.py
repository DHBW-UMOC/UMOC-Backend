import uuid

from flask import Blueprint, request, jsonify

from api.database import databaseManager

endpointApp = Blueprint('main', __name__)


##########################
## REST-API ENDPOINTS
##########################
@endpointApp.route("/register", methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    # public_key = request.form.get('public_key')

    if not username: return jsonify({"error": "No username provided for register"}), 400
    if not password: return jsonify({"error": "No password provided for register"}), 400
    # if not public_key: return jsonify({"error": "No public key provided for register"}), 400

    databaseManager.addUser(username, password, "")

    return "User registered!"


@endpointApp.route("/login", methods=['GET'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username: return jsonify({"error": "No username provided for register"}), 400
    if not password: return jsonify({"error": "No password provided for register"}), 400

    sessionID = uuid.uuid4()
    databaseManager.setSessionId(username, password, sessionID)

    return "User registered!"


@endpointApp.route("/logout", methods=['POST'])
def logout():
    sessionID = request.form.get('sessionID')

    if not sessionID: return jsonify({"error": "No sessionID provided for logout"}), 400

    databaseManager.resetSessionId(sessionID)

    return "User registered!"


@endpointApp.route("/addContact", methods=['POST'])
def addContact():
    sessionID = request.form.get('sessionID')
    contact = request.form.get('contact')

    if not sessionID: return jsonify({"error": "No sessionID provided for addContact"}), 400
    if not contact: return jsonify({"error": "No contact provided for addContact"}), 400

    databaseManager.addContact(sessionID, contact)

    return "User registered!"


@endpointApp.route("/changeContact", methods=['POST'])
def changeContact():
    sessionID = request.form.get('sessionID')
    contact = request.form.get('contact')
    status = request.form.get('status')

    if not sessionID: return jsonify({"error": "No sessionID provided for changeContact"}), 400
    if not contact: return jsonify({"error": "No contact provided for changeContact"}), 400
    if not status: return jsonify({"error": "No status provided for changeContact"}), 400

    databaseManager.changeContact(sessionID, contact, status)

    return "User registered!"


##########################
## TEST ENDPOINTS
##########################
@endpointApp.route("/")
def default():
    return "Hello World"


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

@endpointApp.route("/getContacts")
def getContacts():
    return "Not IMPLEMENTED"
