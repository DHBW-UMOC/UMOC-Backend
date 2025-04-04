# UMOC API Documentation

**Base URL**: `http://localhost:5000`

## Table of Contents
- [Authentication Flow](#authentication-flow)
- [API Endpoints](#api-endpoints)
- [WebSocket Interface](#websocket-interface-specification)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Testing](#testing)

## Authentication Flow

1. Register a user account via `/register`
2. Login to receive a `sessionID` via `/login`
3. Include this `sessionID` in all subsequent API calls and WebSocket connections
4. Use `/logout` to terminate a session

**Session ID Format**: UUIDv4 string (e.g., `"550e8400-e29b-41d4-a716-446655440000"`)

## API Endpoints

### User Registration

**Endpoint**: `/register`  
**Method**: `POST`  
**Description**: Register a new user account.

**Request**:
```json
{
  "username": "johndoe",
  "password": "password123"
}
```

**Response**:
```json
{
  "user_id": 123,
  "username": "johndoe",
  "created_at": "2023-01-01T12:00:00Z"
}
```

### User Login

**Endpoint**: `/login`  
**Method**: `POST`  
**Description**: Login to an existing user account.

**Request**:
```json
{
  "username": "johndoe",
  "password": "password123"
}
```

**Response**:
```json
{
  "sessionID": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 123,
  "username": "johndoe",
  "session_expires": 1636754321
}
```

### User Logout

**Endpoint**: `/logout`  
**Method**: `POST`  
**Description**: Logout from the current session.

**Request**:
```json
{
  "sessionID": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response**:
```json
{
  "message": "Successfully logged out"
}
```

### Get User Info

**Endpoint**: `/user`  
**Method**: `GET`  
**Description**: Retrieve information about the current user.

**Request**:
```json
{
  "sessionID": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response**:
```json
{
  "user_id": 123,
  "username": "johndoe",
  "created_at": "2023-01-01T12:00:00Z"
}
```

## WebSocket Interface Specification

**Base URL**: `ws://localhost:5000/socket.io/`

### General Notes
- **Protocol**: WebSocket using Socket.IO
- **Connection Query Parameter**: `sessionID` (required for authentication)
- **Test Clients**: 
  - Basic: `test/testWebsockets.html` 
  - Advanced: `websocket_test.html` (includes comprehensive testing UI)

### Implemented Features

#### Connection Events
- **connect**: Establish connection with authentication via session ID
- **disconnect**: Terminate connection
- **connect_error**: Handle connection failures

#### Messaging
- **send_message**: Send messages to contacts
- **new_message**: Receive message broadcasts

#### Contact Management
- **add_contact**: Add contacts by username
- **contact_added**: Receive confirmation when contact is added
- **contact_request**: Receive notification when added as a contact

#### User Status
- **user_status**: Receive notifications when contacts come online or go offline

### Implementation Details

#### 1. Connect
**Description**: Establish a connection to the WebSocket server.  
**Query Parameters**:
- `sessionID` (string, required): A valid session ID for the user.  
  Example: `"550e8400-e29b-41d4-a716-446655440000"`

**Client Example**:
```javascript
const socket = io('http://localhost:5000', {
    query: { sessionID: 'valid-session-id' },
    transports: ['websocket', 'polling']
});

socket.on('connect', () => {
    console.log('Connected successfully!');
});

socket.on('connect_error', (error) => {
    console.log(`Connection error: ${error.message}`);
});
```

**Server Implementation Details**:
- Verifies the session ID against active sessions
- Marks the user as online in the database
- Joins the user to chat rooms for all their contacts
- Notifies contacts that the user is now online

#### 2. Disconnect
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

**Server Implementation Details**:
- Removes the connection from active sockets
- Marks user as offline in the database
- Tracks last seen timestamp
- Notifies contacts that user is offline

#### 3. Send Message
**Event name**: `send_message`  
**Description**: Send a new message to a recipient.

**Parameters**:
```javascript
{
    sessionID: "string",  // The session ID of the sender
    recipient_id: "string",  // The recipient's user ID
    content: "string",  // The content of the message
    type: "text|image|item",  // Message type
    is_group: false  // Whether this is a group message
}
```

**Client Example**:
```javascript
socket.emit('send_message', {
    sessionID: 'valid-session-id',
    recipient_id: 'recipient-user-id',
    content: 'Hello, how are you?',
    type: 'text',
    is_group: false
});
```

**Server Implementation Details**:
- Authenticates the sender via session ID
- Validates that the recipient exists
- Ensures the sender and recipient are contacts
- Creates a message with a unique UUID
- Stores the message in the database
- Broadcasts the message to the appropriate room

#### 4. Receive Message
**Event name**: `new_message`  
**Description**: Event fired when a new message is received.

**Data Structure**:
```javascript
{
    message_id: "string",
    sender_id: "string",
    sender_username: "string",
    recipient_id: "string",
    content: "string",
    type: "text|image|item",
    timestamp: "ISO datetime",
    is_group: false
}
```

**Client Example**:
```javascript
socket.on('new_message', (message) => {
    console.log('New message received:', message);
    // Update UI with the new message
});
```

**Server Implementation Details**:
- Messages are broadcast to a room that includes both sender and recipient
- For direct messages, room ID format: `dm_{smaller_user_id}_{larger_user_id}`
- For group messages (not fully implemented), room ID format: `group_{group_id}`

#### 5. Add Contact
**Event name**: `add_contact`  
**Description**: Add a new contact to the user's contact list.

**Parameters**:
```javascript
{
    sessionID: "string",  // The session ID of the user
    contact_username: "string"  // The username of the contact to add
}
```

**Client Example**:
```javascript
socket.emit('add_contact', {
    sessionID: 'valid-session-id',
    contact_username: 'friend_username'
});
```

**Server Implementation Details**:
- Verifies the session and retrieves the user
- Looks up the contact by username
- Checks if contact relationship already exists
- Creates a new contact relationship with status "NEW"
- Stores contact in database with streak information

#### 6. Contact Added Confirmation
**Event name**: `contact_added`  
**Description**: Event fired when a contact is successfully added.

**Data Structure**:
```javascript
{
    user_id: "string",
    username: "string",
    status: "NEW"
}
```

**Client Example**:
```javascript
socket.on('contact_added', (data) => {
    console.log('Contact added:', data);
    // Update UI to show the new contact
});
```

**Server Implementation Details**:
- Sent to the user who initiated the add contact operation
- Contains basic information about the newly added contact

#### 7. Contact Request
**Event name**: `contact_request`  
**Description**: Event fired when another user adds you as a contact.

**Data Structure**:
```javascript
{
    user_id: "string",
    username: "string"
}
```

**Client Example**:
```javascript
socket.on('contact_request', (data) => {
    console.log('New contact request:', data);
    // Show notification for new contact request
});
```

**Server Implementation Details**:
- Sent to the user who was added as a contact
- Contains information about who added them

#### 8. User Status Update
**Event name**: `user_status`  
**Description**: Event fired when a contact's online status changes.

**Data Structure**:
```javascript
{
    user_id: "string",
    username: "string",
    status: "online" | "offline",
    last_seen: "ISO datetime"  // Only included for offline status
}
```

**Client Example**:
```javascript
socket.on('user_status', (data) => {
    console.log('User status update:', data);
    // Update UI to reflect the contact's online status
});
```

**Server Implementation Details**:
- Triggered when users connect or disconnect
- Notifies all contacts of the user's new status
- Includes last seen timestamp for offline status

## Data Models

### User

```json
{
  "user_id": 123,
  "username": "johndoe",
  "created_at": "2023-01-01T12:00:00Z"
}
```

### Session

```json
{
  "sessionID": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 123,
  "username": "johndoe",
  "session_expires": 1636754321
}
```

### Chat

```json
{
  "id": 456,
  "username": "janedoe",  // For direct messages
  "status": "online",
  "last_seen": "2023-01-01T12:00:00Z",
  "last_message": {
    "message_id": "msg-uuid-here",
    "sender_id": 123,
    "sender_username": "johndoe",
    "content": "Hello there!",
    "type": "text",
    "timestamp": "2023-01-01T12:00:00Z"
  },
  "unread_count": 3,
  "is_group": false
}
```

### Message

```json
{
  "message_id": "msg-uuid-here",
  "sender_id": 123,
  "sender_username": "johndoe",
  "recipient_id": 456,
  "content": "Hello there!",
  "type": "text",
  "timestamp": "2023-01-01T12:00:00Z",
  "is_group": false
}
```

## Error Handling

### Common Errors

**Error Code**: `400`  
**Description**: Bad Request - The request could not be understood or was missing required parameters.

**Error Code**: `401`  
**Description**: Unauthorized - Authentication failed or user does not have permissions for the requested operation.

**Error Code**: `403`  
**Description**: Forbidden - Authentication succeeded but authenticated user does not have access to the requested resource.

**Error Code**: `404`  
**Description**: Not Found - The requested resource could not be found.

**Error Code**: `500`  
**Description**: Internal Server Error - An error occurred on the server.

## Testing

### Unit Tests

Unit tests are written using the `unittest` framework. To run the tests, use the following command:

```bash
python -m unittest discover tests
```

### Integration Tests

Integration tests are written using the `pytest` framework. To run the tests, use the following command:

```bash
pytest tests/integration
```

### End-to-End Tests

End-to-end tests are written using the `selenium` framework. To run the tests, use the following command:

```bash
pytest tests/e2e
```

The backend includes enhanced security features for WebSocket connections:

1. **Token Verification**: Additional HMAC-based token verification
2. **Rate Limiting**: Prevents abuse of the WebSocket API
3. **Session Management**: Automatic cleanup of expired sessions
4. **Input Validation**: All handlers validate input data
5. **Secure File Uploads**: Two-step process with token verification

The backend repository includes two test clients that can be used to test the WebSocket interface:

1. **Basic Test Client**: `test/testWebsockets.html`
   - Simple interface for testing core functionality
   - Focused on basic connection and messaging tests

2. **Advanced Test Client**: `websocket_test.html`
   - Comprehensive testing interface with support for all implemented features
   - Includes user profile management and reconnection handling
   - Provides visual feedback for message history

To use either test client:

1. Start the backend server
2. Open the HTML file in a browser
3. Use the form to connect with a valid session ID
4. Test sending messages and other interactions

The WebSocket implementation uses Socket.IO which provides:
- Automatic reconnection capabilities
- Transport fallback (WebSocket → HTTP long-polling)
- Event-based communication model