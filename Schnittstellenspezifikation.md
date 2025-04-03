# UMOC API Documentation

Base URL: `http://localhost:5000`

## Table of Contents
- [Authentication Flow](#authentication-flow)
- [API Endpoints](#api-endpoints)
- [WebSocket Interface](#websocket-interface-specification)
- [Data Models](#data-models)
- [Error Handling](#error-handling)

## Authentication Flow

1. Register a user account via `/register`
2. Login to receive a `sessionID` via `/login`
3. Include this `sessionID` in all subsequent API calls and WebSocket connections
4. Use `/logout` to terminate a session

**Session ID Format**: UUIDv4 string (e.g., `"{session_id}"`)

## API Endpoints

### 1. Register a User
**Endpoint**: `/register`  
**Method**: `POST`  
**Content-Type**: `application/json`

**Request Body**:
```json
{
    "username": "{username}",
    "password": "{password}"
}
```

**Successful Response** (200 OK):
```json
{
    "success": "User registered successfully",
    "user_id": "{user_id}"
}
```

**Error Responses**:
- Missing username (400 Bad Request):
  ```json
  {
      "error": "No username provided for register"
  }
  ```
- Username already exists (409 Conflict):
  ```json
  {
      "error": "Username already exists"
  }
  ```
- Missing password (400 Bad Request):
  ```json
  {
      "error": "No password provided for register"
  }
  ```

### 2. Login a User
**Endpoint**: `/login`  
**Method**: `POST`  
**Content-Type**: `application/json`

**Request Body**:
```json
{
    "username": "{username}",
    "password": "{password}",
    "public_key": "{public_key}"  // Optional
}
```

**Successful Response** (200 OK):
```json
{
    "success": "User logged in, session ID created",
    "sessionID": "{session_id}",
    "user_id": "{user_id}"
}
```

**Error Responses**:
- Missing username (400 Bad Request):
  ```json
  {
      "error": "No username provided for login"
  }
  ```
- Missing password (400 Bad Request):
  ```json
  {
      "error": "No password provided for login"
  }
  ```
- Invalid credentials (401 Unauthorized):
  ```json
  {
      "error": "Invalid username or password"
  }
  ```

### 3. Logout a User
**Endpoint**: `/logout`  
**Method**: `POST`  
**Content-Type**: `application/json`

**Request Body**:
```json
{
    "sessionID": "{session_id}"
}
```

**Successful Response** (200 OK):
```json
{
    "success": "User logged out successfully"
}
```

**Error Responses**:
- Missing sessionID (400 Bad Request):
  ```json
  {
      "error": "No sessionID provided for logout"
  }
  ```
- Invalid sessionID (401 Unauthorized):
  ```json
  {
      "error": "Invalid session ID"
  }
  ```

### 4. Add a Contact
**Endpoint**: `/addContact`  
**Method**: `POST`  
**Content-Type**: `application/json`

**Request Body**:
```json
{
    "sessionID": "{session_id}",
    "contactID": "{contact_id}"
}
```

**Successful Response** (200 OK):
```json
{
    "success": "Contact added successfully",
    "contact": {
        "contact_id": "{contact_id}",
        "name": "{contact_username}",
        "status": "new",
        "url": "{profile_image_url}"
    }
}
```

**Error Responses**:
- Missing sessionID (400 Bad Request):
  ```json
  {
      "error": "No sessionID provided for addContact"
  }
  ```
- Invalid sessionID (401 Unauthorized):
  ```json
  {
      "error": "Invalid session ID"
  }
  ```
- Missing contactID (400 Bad Request):
  ```json
  {
      "error": "No contactID provided for addContact"
  }
  ```
- Contact not found (404 Not Found):
  ```json
  {
      "error": "Contact not found"
  }
  ```
- Contact already added (409 Conflict):
  ```json
  {
      "error": "Contact already exists"
  }
  ```

### 5. Change Contact Status
**Endpoint**: `/changeContact`  
**Method**: `POST`  
**Content-Type**: `application/json`

**Request Body**:
```json
{
    "sessionID": "{session_id}",
    "contact": "{contact_id}",
    "status": "{status}"  // Possible values: "friend", "blocked", "new", "timeout", "last_words"
}
```

**Successful Response** (200 OK):
```json
{
    "success": "Contact status changed successfully",
    "contact": {
        "contact_id": "{contact_id}",
        "name": "{contact_username}",
        "status": "{status}"
    }
}
```

**Error Responses**:
- Missing sessionID (400 Bad Request):
  ```json
  {
      "error": "No sessionID provided for changeContact"
  }
  ```
- Missing contact (400 Bad Request):
  ```json
  {
      "error": "No contact provided for changeContact"
  }
  ```
- Invalid status (400 Bad Request):
  ```json
  {
      "error": "Invalid status provided"
  }
  ```
- Contact not found (404 Not Found):
  ```json
  {
      "error": "Contact not found"
  }
  ```

### 6. Get Contacts
**Endpoint**: `/getContacts`  
**Method**: `GET`  
**Query Parameters**:
- `sessionID` (string, required): The session ID of the user

**Example Request**:
```
GET /getContacts?sessionID={session_id}
```

**Successful Response** (200 OK):
```json
{
    "contacts": [
        {
            "contact_id": "{contact_id_1}",
            "name": "{contact_username_1}",
            "status": "friend",
            "streak": 1,
            "url": "{profile_image_url_1}",
            "is_online": true
        },
        {
            "contact_id": "{contact_id_2}",
            "name": "{contact_username_2}",
            "status": "new",
            "streak": 0,
            "url": "{profile_image_url_2}",
            "is_online": false
        }
    ]
}
```

**Error Responses**:
- Missing sessionID (400 Bad Request):
  ```json
  {
      "error": "No sessionID provided for getContacts"
  }
  ```
- Invalid sessionID (401 Unauthorized):
  ```json
  {
      "error": "Invalid session ID"
  }
  ```

### 7. Get Contact Messages
**Endpoint**: `/getContactMessages`  
**Method**: `GET`  
**Query Parameters**:
- `sessionID` (string, required): The session ID of the user
- `contactID` (string, required): The contact's user ID

**Example Request**:
```
GET /getContactMessages?sessionID={session_id}&contactID={contact_id}
```

**Successful Response** (200 OK):
```json
{
    "messages": [
        {
            "message_id": "{message_id_1}",
            "content": "{message_content_1}",
            "type": "text",
            "send_at": "{timestamp_1}",
            "sender_user_id": "{sender_id_1}",
            "is_group": false
        },
        {
            "message_id": "{message_id_2}",
            "content": "{message_content_2}",
            "type": "text",
            "send_at": "{timestamp_2}",
            "sender_user_id": "{sender_id_2}",
            "is_group": false
        }
    ]
}
```

**Error Responses**:
- Missing sessionID (400 Bad Request):
  ```json
  {
      "error": "No sessionID provided for getContactMessages"
  }
  ```
- Missing contactID (400 Bad Request):
  ```json
  {
      "error": "No contactID provided for getContactMessages"
  }
  ```
- Invalid sessionID (401 Unauthorized):
  ```json
  {
      "error": "Invalid session ID"
  }
  ```
- Contact not found (404 Not Found):
  ```json
  {
      "error": "Contact not found"
  }
  ```

### 8. Save Message
**Endpoint**: `/saveMessage`  
**Method**: `POST`  
**Content-Type**: `application/json`

**Request Body**:
```json
{
    "sessionID": "{session_id}",
    "recipientID": "{recipient_id}",
    "content": "{message_content}",
    "type": "{message_type}",
    "is_group": false
}
```

**Successful Response** (200 OK):
```json
{
    "success": "Message saved successfully",
    "message_id": "{message_id}",
    "timestamp": "{timestamp}"
}
```

**Error Responses**:
- Missing sessionID (400 Bad Request):
  ```json
  {
      "error": "No sessionID provided for saveMessage"
  }
  ```
- Missing recipientID (400 Bad Request):
  ```json
  {
      "error": "No recipientID provided for saveMessage"
  }
  ```
- Missing content (400 Bad Request):
  ```json
  {
      "error": "No content provided for saveMessage"
  }
  ```
- Invalid sessionID (401 Unauthorized):
  ```json
  {
      "error": "Invalid session ID"
  }
  ```
- Recipient not found (404 Not Found):
  ```json
  {
      "error": "Recipient not found"
  }
  ```

## WebSocket Interface Specification

Base URL: `http://localhost:5000`

### General Notes
- **Protocol**: WebSocket using Socket.IO
- **Connection Query Parameter**: `sessionID` (required for authentication)
- **Prototype**: `test/testWebSockets.html`

### Event Types Overview
1. **Connection Events**: `connect`, `disconnect`, `connect_error`
2. **Message Events**: `send_message`, `new_message`
3. **Contact Events**: `add_contact`, `contact_added`, `contact_request`
4. **Status Events**: `user_status`

### 1. Connect
**Description**: Establish a connection to the WebSocket server.  
**Query Parameters**:
- `sessionID` (string, required): A valid session ID for the user.  
  Example: `"{session_id}"`

**Client Example**:
```javascript
const socket = io('http://localhost:5000', {
    query: { sessionID: '{session_id}' },
    transports: ['websocket', 'polling']
});

socket.on('connect', () => {
    console.log('Connected successfully!');
});

socket.on('connect_error', (error) => {
    console.log(`Connection error: ${error.message}`);
});
```

### 2. Disconnect
**Event name**: `disconnect`  
**Description**: Terminates the WebSocket connection.

**Client Example**:
```javascript
socket.disconnect();

// OR to monitor disconnection
socket.on('disconnect', (reason) => {
    console.log(`Disconnected: ${reason}`);
});
```

### 3. Send Message
**Event name**: `send_message`  
**Description**: Send a new message to a recipient.

**Parameters**:
```javascript
{
    sessionID: "{session_id}",  // The session ID of the sender
    recipient_id: "{recipient_id}",  // The recipient's user ID
    content: "{message_content}",  // The content of the message
    type: "{message_type}",  // Message type: "text", "image", or "item"
    is_group: false  // Whether this is a group message
}
```

**Client Example**:
```javascript
socket.emit('send_message', {
    sessionID: '{session_id}',
    recipient_id: '{recipient_id}',
    content: '{message_content}',
    type: '{message_type}',
    is_group: false
});
```

### 4. Receive Message
**Event name**: `new_message`  
**Description**: Event fired when receiving a new message.

**Data Structure**:
```javascript
{
    message_id: "{message_id}",  // Unique message ID
    sender_id: "{sender_id}",  // Sender's user ID
    sender_username: "{sender_username}",  // Sender's username
    content: "{message_content}",  // Message content
    type: "{message_type}",  // Message type: "text", "image", or "item"
    timestamp: "{timestamp}",  // When the message was sent
    is_group: false  // Whether this is a group message
}
```

**Client Example**:
```javascript
socket.on('new_message', (data) => {
    console.log('New message received:', data);
    // Handle the new message (e.g., display it in the UI)
});
```

### 5. Add Contact
**Event name**: `add_contact`  
**Description**: Add a new contact to the user's contact list.

**Parameters**:
```javascript
{
    sessionID: "{session_id}",  // The session ID of the user
    contact_username: "{contact_username}"  // The username of the contact to add
}
```

**Client Example**:
```javascript
socket.emit('add_contact', {
    sessionID: '{session_id}',
    contact_username: '{contact_username}'
});
```

### 6. Contact Added Confirmation
**Event name**: `contact_added`  
**Description**: Event fired when a contact is successfully added.

**Data Structure**:
```javascript
{
    success: true,
    contact: {
        contact_id: "{contact_id}",
        name: "{contact_username}",
        status: "new",
        url: "{profile_image_url}",
        is_online: false
    }
}
```

**Client Example**:
```javascript
socket.on('contact_added', (data) => {
    console.log('Contact added:', data);
    // Update UI to show the new contact
});
```

### 7. Contact Request
**Event name**: `contact_request`  
**Description**: Event fired when another user adds you as a contact.

**Data Structure**:
```javascript
{
    from_user_id: "{user_id}",
    from_username: "{username}",
    timestamp: "{timestamp}"
}
```

**Client Example**:
```javascript
socket.on('contact_request', (data) => {
    console.log('New contact request:', data);
    // Show notification for new contact request
});
```

### 8. User Status Update
**Event name**: `user_status`  
**Description**: Event fired when a contact's online status changes.

**Data Structure**:
```javascript
{
    user_id: "{user_id}",
    username: "{username}",
    is_online: true,
    last_seen: "{timestamp}"  // Only included when is_online is false
}
```

**Client Example**:
```javascript
socket.on('user_status', (data) => {
    console.log('User status update:', data);
    // Update UI to reflect the contact's online status
});
```

## Data Models

### 1. User
```typescript
interface User {
    user_id: string;  // UUID
    username: string;
    session_id: string | null;  // UUID or null if not logged in
    created_at: string;  // ISO datetime
    is_online: boolean;
}
```

### 2. Contact
```typescript
interface Contact {
    contact_id: string;  // UUID of the contact user
    name: string;  // Username of the contact
    status: "friend" | "last_words" | "blocked" | "new" | "timeout";
    streak: number;  // Number of consecutive days with messages
    url: string;  // Profile image URL
    is_online: boolean;
}
```

### 3. Message
```typescript
interface Message {
    message_id: string;  // UUID
    sender_user_id: string;  // UUID
    recipient_user_id: string;  // UUID
    content: string;  // Encrypted message content
    type: "text" | "image" | "item";
    send_at: string;  // ISO datetime
    updated_at: string;  // ISO datetime
    is_group: boolean;
}
```

### 4. Item Types
```typescript
type ItemType = "mute" | "lightmode" | "kick";
```

## Error Handling

### HTTP Status Codes
- **200 OK**: Request processed successfully
- **400 Bad Request**: Missing required parameters
- **401 Unauthorized**: Invalid session ID or credentials
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource already exists
- **500 Internal Server Error**: Unexpected server error

### WebSocket Error Handling
- **connect_error**: Connection could not be established
- **error**: General error during WebSocket communication

### Best Practices
1. Always check the returned JSON for an `error` key
2. Handle WebSocket disconnections gracefully
3. Implement retry logic for failed connections
4. Monitor and log error messages for debugging

## Testing

The backend repository includes a test client (`testWebsockets.html`) that can be used to test the WebSocket interface. To use it:

1. Start the backend server
2. Open the HTML file in a browser
3. Use the form to connect with a valid session ID
4. Test sending messages and other interactions