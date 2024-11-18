# To sync the packages run 
```
pip freeze > requirements.txt
```
# Usage

Run the main.py file. Maybe sync the packages first.
The server will be running on localhost:5000

# API & WebSocket Interface Specification

## REST-API Endpoints

### 1. Register User
**Endpoint:** `/register`  
**Method:** `POST`  
**Parameters:**
- `username` (string, required): The username for the new user.
- `password` (string, required): The password for the new user.
- `public_key` (string, optional, currently unused).

**Response:**
- **200 OK**: User registered successfully.
- **400 Bad Request**: Error if `username` or `password` is not provided.

---

### 2. Login User
**Endpoint:** `/login`  
**Method:** `GET`  
**Parameters:**
- `username` (string, required): The username of the user.
- `password` (string, required): The password of the user.

**Response:**
- **200 OK**: User logged in, session ID created.
- **400 Bad Request**: Error if `username` or `password` is not provided.

---

### 3. Logout User
**Endpoint:** `/logout`  
**Method:** `POST`  
**Parameters:**
- `sessionID` (string, required): The session ID of the user.

**Response:**
- **200 OK**: User logged out successfully.
- **400 Bad Request**: Error if `sessionID` is not provided.

---

### 4. Add Contact
**Endpoint:** `/addContact`  
**Method:** `POST`  
**Parameters:**
- `sessionID` (string, required): The session ID of the user.
- `contact` (string, required): The contact's username.

**Response:**
- **200 OK**: Contact added successfully.
- **400 Bad Request**: Error if `sessionID` or `contact` is not provided.

---

### 5. Change Contact Status
**Endpoint:** `/changeContact`  
**Method:** `POST`  
**Parameters:**
- `sessionID` (string, required): The session ID of the user.
- `contact` (string, required): The contact's username.
- `status` (string, required): The new status of the contact.

**Response:**
- **200 OK**: Contact status changed successfully.
- **400 Bad Request**: Error if any parameter is missing.

---

### 6. Get Contacts
**Endpoint:** `/getContacts`  
**Method:** `GET`  
**Parameters:**
- `sessionID` (string, required): The session ID of the user.

**Response:**
- **200 OK**: Returns a list of contacts.
- **400 Bad Request**: Error if `sessionID` is not provided.

---

### 7. Get Contact Messages
**Endpoint:** `/getContactMessages`  
**Method:** `GET`  
**Parameters:**
- `sessionID` (string, required): The session ID of the user.
- `contact` (string, required): The contact's username.

**Response:**
- **200 OK**: Returns messages between the user and the contact.
- **400 Bad Request**: Error if any parameter is missing.

---

### 8. Default Test Endpoint
**Endpoint:** `/`  
**Method:** `GET`  
**Response:** 
- **200 OK**: "Hello World"

---

## WebSocket Endpoints

### 1. Connect
**Event:** `connect`  
**Parameters:**
- `sessionID` (string, required): The session ID of the user.

**Behavior:**
- Joins the user to rooms based on their contacts and group memberships.
- Notifies contacts that the user is online.

**Error Handling:**
- Returns `False` if `session_id` is missing or user is not found.

---

### 2. Disconnect
**Event:** `disconnect`  
**Parameters:**
- `sessionID` (string, required): The session ID of the user.

**Behavior:**
- Marks the user as offline and notifies their contacts.

---

### 3. Send Message
**Event:** `send_message`  
**Parameters:**
- `sessionID` (string, required): The session ID of the sender.
- `recipient_id` (int, required): The ID of the message recipient.
- `content` (string, required): The message content.
- `is_group` (boolean, optional): Specifies if the message is for a group.
- `type` (string, optional, default: 'text'): The type of message.

**Behavior:**
- Stores the message and emits it to the appropriate room.

---

### 4. Add Contact
**Event:** `add_contact`  
**Parameters:**
- `sessionID` (string, required): The session ID of the user.
- `contact_username` (string, required): The username of the contact to add.

**Behavior:**
- Adds a contact relationship and notifies both users.

**Error Handling:**
- Emits an `error` if the contact is not found.
