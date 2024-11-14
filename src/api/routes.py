from src.database.databaseManager import db
from src.database.models import User, Group
from flask import Flask, jsonify, request
from src.database import databaseManager

app = Flask(__name__)


###########################
## REST-API ENDPOINTS
##########################
@app.route("/login", methods=['GET', 'POST'])
def login():
    pass


@app.route("/saveMessage", methods=["POST"])
def saveMessage():
    # if not is_authenticated(request.headers.get('Authorization')):
    #     return jsonify({"error": "Unauthorized"}), 401
    #
    # message_data = request.get_json()
    # if message_data and 'message' in message_data:
    #     # Assuming databaseManager.save_message accepts a message and saves it
    #     senderUserId = session.get('username', 'Anonymous')  # Placeholder for actual user identification
    #     databaseManager.InsertMessage(senderUserId, message_data['message'])
    #     return jsonify({"status": "Message saved"}), 200
    # else:
    #     return jsonify({"error": "Invalid message data"}), 400
    pass

@app.route("/getMessages")
def getMessage():
    # if not is_authenticated(request.headers.get('Authorization')):
    #     return jsonify({"error": "Unauthorized"}), 401
    #
    # # Example of retrieving messages for a specific group (assuming Group1 here)
    # messages = databaseManager.getMessage("10.11.2024", "10.11.2024",
    #                                       "Group1")  # Modify as per databaseManager function
    # return jsonify(messages), 200
    pass