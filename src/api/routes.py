import uuid

from api.database import databaseManager
from flask import Blueprint, request, jsonify

endpointApp = Blueprint('main', __name__)


##########################
## REST-API ENDPOINTS
##########################
@endpointApp.route("/register", methods=['POST'])
def register():
    username = request.args.get('username')
    password = request.args.get('password')
    # public_key = request.form.get('public_key')

    if not username: return jsonify({"error": "No username provided for register"}), 400
    if not password: return jsonify({"error": "No password provided for register"}), 400
    # if not public_key: return jsonify({"error": "No public key provided for register"}), 400

    databaseManager.addUser(username, password, "")

    return jsonify({"success": "No username provided for register"})


@endpointApp.route("/login", methods=['GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')

    if not username: return jsonify({"error": "No username provided for login"}), 400
    if not password: return jsonify({"error": "No password provided for login"}), 400

    sessionID = str(uuid.uuid4())
    if not databaseManager.setSessionId(username, password, sessionID):
        return jsonify({"error": "User not found. Username or password is wrong...Probably"}), 400

    return jsonify({"sessionID": str(sessionID)})


@endpointApp.route("/logout", methods=['POST'])
def logout():
    sessionID = request.args.get('sessionID')

    if not sessionID: return jsonify({"error": "No sessionID provided for logout"}), 400

    databaseManager.resetSessionId(sessionID)

    return jsonify({"success": "User logged out successfully"})


@endpointApp.route("/addContact", methods=['POST'])
def addContact():
    sessionID = request.args.get('sessionID')
    contact = request.args.get('contactID')

    if not sessionID: return jsonify({"error": "No sessionID provided for addContact"}), 400
    if not contact: return jsonify({"error": "No contact provided for addContact"}), 400

    if not databaseManager.addContact(sessionID, contact):
        return jsonify({"error": "User not found. SessionID is wrong...Probably"}), 400

    return jsonify({"success": "Contact was added successfully"})


@endpointApp.route("/changeContact", methods=['POST'])
def changeContact():
    sessionID = request.args.get('sessionID')
    contact = request.args.get('contactID')
    status = request.args.get('status')

    if not sessionID: return jsonify({"error": "No sessionID provided for changeContact"}), 400
    if not contact: return jsonify({"error": "No contact provided for changeContact"}), 400
    if not status: return jsonify({"error": "No status provided for changeContact"}), 400

    if not databaseManager.changeContact(sessionID, contact, status):
        return jsonify({"error": "User not found. SessionID is wrong...Probably"}), 400

    return "User registered!"


@endpointApp.route("/getContacts", methods=['GET'])
def getContacts():
    sessionID = request.args.get('sessionID')

    if not sessionID: return jsonify({"error": "No sessionID provided for getContacts"}), 400

    return databaseManager.getContacts(sessionID)


@endpointApp.route("/getContactMessages", methods=['GET'])
def getContactMessages():
    sessionID = request.args.get('sessionID')
    contactID = request.args.get('contactID')

    if not sessionID: return jsonify({"error": "No sessionID provided for getContactMessages"}), 400
    if not contactID: return jsonify({"error": "No contact provided for getContactMessages"}), 400

    return databaseManager.getContactMessages(sessionID, contactID)


##########################
## TEST ENDPOINTS
##########################
@endpointApp.route("/")
def default():
    return "Hello World"


@endpointApp.route("/saveMessage", methods=["POST"])
def saveMessage():

    data = request.json

    sessionID = data["sessionID"]
    recipientID = data["recipientID"]
    content = data["content"]

    if not sessionID:
        return jsonify({"error": "No message provided"}), 400

    return databaseManager.saveMessage(sessionID, recipientID, content)


# @endpointApp.route("/getMessages")
# def getMessage():
#     return databaseManager.getMessages()
