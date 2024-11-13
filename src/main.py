from flask import Flask, request, session, redirect, jsonify, url_for
from flask_socketio import SocketIO

import databaseManager
import resource.config as config

###########################
## SETUP
###########################
app = Flask(__name__)
app.secret_key = config.getKey()
AUTH_TOKENS = {'user_token': 'secure_token_here'}

socketio = SocketIO(app, cors_allowed_origins="*")


###########################
## HELPER FUNCTIONS
###########################
def is_authenticated(token):
    """ Check if provided token is valid. """
    return token in AUTH_TOKENS.values()


###########################
## REST-API ENDPOINTS
###########################
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('helloWorld'))
    return '''
        <form method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''


@app.route("/helloWorld")
def helloWorld():
    if 'username' in session:
        return f"<p>Hello, {session['username']}!</p>"
    return 'You are not logged in'


@app.route("/saveMessage", methods=["POST"])
def saveMessage():
    if not is_authenticated(request.headers.get('Authorization')):
        return jsonify({"error": "Unauthorized"}), 401

    message_data = request.get_json()
    if message_data and 'message' in message_data:
        # Assuming databaseManager.save_message accepts a message and saves it
        senderUserId = session.get('username', 'Anonymous')  # Placeholder for actual user identification
        databaseManager.InsertMessage(senderUserId, message_data['message'])
        return jsonify({"status": "Message saved"}), 200
    else:
        return jsonify({"error": "Invalid message data"}), 400


@app.route("/getMessages")
def getMessage():
    if not is_authenticated(request.headers.get('Authorization')):
        return jsonify({"error": "Unauthorized"}), 401

    # Example of retrieving messages for a specific group (assuming Group1 here)
    messages = databaseManager.getMessage("10.11.2024", "10.11.2024",
                                          "Group1")  # Modify as per databaseManager function
    return jsonify(messages), 200


###########################
## WEBSOCKET ENDPOINTS
###########################
@socketio.on('connect')
def handle_connect():
    pass


@socketio.on('disconnect')
def handle_disconnect():
    pass


###########################
## MAIN FUNCTION
###########################
if __name__ == "__main__":
    app.run()
