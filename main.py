from flask import Flask, url_for, request, session, redirect, jsonify
import databaseManager  # Ensure this has the necessary functions implemented

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Dummy in-memory token for simplicity (replace with a database-backed system for production)
AUTH_TOKENS = {'user_token': 'secure_token_here'}  # Replace 'secure_token_here' with an actual secure token

def is_authenticated(token):
    """ Check if provided token is valid. """
    return token in AUTH_TOKENS.values()

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
        databaseManager.InsertMessage(session.get('username'), message_data['message'])
        return jsonify({"status": "Message saved"}), 200
    else:
        return jsonify({"error": "Invalid message data"}), 400

@app.route("/getMessages")
def getMessage():
    if not is_authenticated(request.headers.get('Authorization')):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Example of retrieving messages for a specific group (assuming Group1 here)
    messages = databaseManager.getMessage("", "", "Group1")  # Modify as per databaseManager function
    return jsonify(messages), 200

if __name__ == "__main__":
    app.run()
