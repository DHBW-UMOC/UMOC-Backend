# UMOC Backend API Specification

## WebSocket Interface Specification

This document outlines the WebSocket API endpoints, event types, and message formats for the UMOC-Backend chat platform.

### Connection Establishment

#### Connecting to the WebSocket Server

To establish a WebSocket connection with authentication:

```
ws://your-server-url/socket.io/?sessionID=<user_session_id>&token=<session_token>
```

Required Query Parameters:
- `sessionID`: The unique session identifier obtained after authentication
- `token`: A session token for additional security verification

### Authentication Events

#### Connection Successful

**Event**: `connection_successful`  
**Direction**: Server → Client  
**Description**: Sent by the server upon successful authentication and connection.

```json
{
  "user_id": 123,
  "username": "johndoe",
  "session_expires": 1636754321
}
```

#### Session Verification

**Event**: `verify_session`  
**Direction**: Client → Server  
**Description**: Used to verify if a session is still valid.

Request:
```json
{
  "sessionID": "session-uuid-here",
  "token": "optional-session-token"
}
```

**Event**: `session_status`  
**Direction**: Server → Client  
**Description**: Response to session verification request.

Response:
```json
{
  "valid": true,
  "expires_at": 1636754321
}
```

Or if invalid:
```json
{
  "valid": false,
  "message": "Your session has expired or is invalid"
}
```

#### Connection Keepalive

**Event**: `ping`  
**Direction**: Client → Server  
**Description**: Keep connection alive and measure latency.

Request:
```json
{
  "sessionID": "session-uuid-here",
  "timestamp": 1636750000000
}
```

**Event**: `pong`  
**Direction**: Server → Client  
**Description**: Server response to ping.

Response:
```json
{
  "timestamp": 1636750000000,
  "server_time": 1636750000100,
  "latency": 100
}
```

### User Status Management

#### User Status Updates

**Event**: `user_status`  
**Direction**: Server → Client  
**Description**: Notifies clients when a contact's status changes.

```json
{
  "user_id": 123,
  "username": "johndoe",
  "status": "online" | "offline",
  "last_seen": "2023-01-01T12:00:00Z"  // Only present for offline status
}
```

### Chat Management

#### Get Chat List

**Event**: `get_chats`  
**Direction**: Client → Server  
**Description**: Request all chats for the current user.

Request:
```json
{
  "sessionID": "session-uuid-here"
}
```

**Event**: `chats`  
**Direction**: Server → Client  
**Description**: List of all user's chats.

Response:
```json
[
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
  },
  {
    "id": 789,
    "name": "Project Team",  // For group chats
    "description": "Team discussion group",
    "member_count": 5,
    "last_message": { /* message object */ },
    "unread_count": 10,
    "is_group": true
  }
]
```

#### Get Chat Info

**Event**: `get_chat_info`  
**Direction**: Client → Server  
**Description**: Get detailed information about a specific chat.

Request:
```json
{
  "sessionID": "session-uuid-here",
  "chat_id": 456,
  "is_group": false
}
```

**Event**: `chat_info`  
**Direction**: Server → Client  
**Description**: Detailed chat information.

Response for direct messages:
```json
{
  "id": 456,
  "username": "janedoe",
  "is_online": true,
  "last_seen": "2023-01-01T12:00:00Z",
  "status": "FRIEND",
  "is_group": false,
  "streak": 3,
  "continue_streak": true
}
```

Response for group chats:
```json
{
  "id": 789,
  "name": "Project Team",
  "description": "Team discussion group",
  "created_at": "2023-01-01T10:00:00Z",
  "is_group": true,
  "members": [
    {
      "user_id": 123,
      "username": "johndoe",
      "is_online": true,
      "last_seen": null,
      "is_admin": true
    },
    // Other members...
  ],
  "member_count": 5,
  "is_admin": true
}
```

#### Get Chat History

**Event**: `get_chat_history`  
**Direction**: Client → Server  
**Description**: Request message history for a specific chat with pagination.

Request:
```json
{
  "sessionID": "session-uuid-here",
  "chat_id": 456,
  "is_group": false,
  "page": 1,
  "page_size": 20
}
```

**Event**: `chat_history`  
**Direction**: Server → Client  
**Description**: Message history for the requested chat.

Response:
```json
{
  "chat_id": 456,
  "is_group": false,
  "messages": [
    {
      "message_id": "msg-uuid-1",
      "sender_id": 123,
      "sender_username": "johndoe",
      "content": "Hello there!",
      "type": "text",
      "timestamp": "2023-01-01T12:00:00Z",
      "is_read": true
    },
    // More messages...
  ],
  "page": 1,
  "total_pages": 5,
  "total_messages": 100
}
```

### Messaging

#### Send Message

**Event**: `send_message`  
**Direction**: Client → Server  
**Description**: Send a new message to a chat.

Request:
```json
{
  "sessionID": "session-uuid-here",
  "recipient_id": 456,
  "content": "Hello there!",
  "is_group": false,
  "type": "text"  // One of: text, image, video, audio, file
}
```

**Event**: `new_message`  
**Direction**: Server → Client  
**Description**: Broadcast of new message to all recipients.

Response:
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

#### Delete Message

**Event**: `delete_message`  
**Direction**: Client → Server  
**Description**: Delete a previously sent message.

Request:
```json
{
  "sessionID": "session-uuid-here",
  "message_id": "msg-uuid-here"
}
```

**Event**: `message_deleted`  
**Direction**: Server → Client  
**Description**: Notification that a message was deleted.

Response:
```json
{
  "message_id": "msg-uuid-here",
  "sender_id": 123,
  "timestamp": "2023-01-02T12:00:00Z"
}
```

#### Read Receipts

**Event**: `read_receipt`  
**Direction**: Client → Server  
**Description**: Mark messages as read and notify sender.

Request:
```json
{
  "sessionID": "session-uuid-here",
  "message_ids": ["msg-uuid-1", "msg-uuid-2"],
  "sender_id": 456
}
```

**Event**: `messages_read`  
**Direction**: Server → Client  
**Description**: Notification that messages were read.

Response (sent to original sender):
```json
{
  "reader_id": 123,
  "reader_username": "johndoe",
  "message_ids": ["msg-uuid-1", "msg-uuid-2"],
  "timestamp": "2023-01-02T12:00:00Z"
}
```

#### Typing Indicators

**Event**: `typing`  
**Direction**: Client → Server  
**Description**: Indicate user is typing or stopped typing.

Request:
```json
{
  "sessionID": "session-uuid-here",
  "recipient_id": 456,
  "is_typing": true,
  "is_group": false
}
```

**Event**: `typing_indicator`  
**Direction**: Server → Client  
**Description**: Broadcast typing status to recipients.

Response:
```json
{
  "user_id": 123,
  "username": "johndoe",
  "is_typing": true,
  "timestamp": 1636750000.123
}
```

### File Sharing

#### Prepare File Upload

**Event**: `upload_file_prepare`  
**Direction**: Client → Server  
**Description**: Request upload URL for file sharing.

Request:
```json
{
  "sessionID": "session-uuid-here",
  "recipient_id": 456,
  "is_group": false,
  "file_name": "image.jpg",
  "file_size": 1024000,
  "file_type": "image/jpeg"
}
```

**Event**: `file_upload_ready`  
**Direction**: Server → Client  
**Description**: Provides secure upload URL.

Response:
```json
{
  "file_id": "file-uuid-here",
  "upload_url": "/api/upload/file-uuid-here",
  "upload_token": "secure-upload-token",
  "expires_in": 3600
}
```

#### Complete File Upload

**Event**: `upload_file_complete`  
**Direction**: Client → Server  
**Description**: Notify server that file upload is complete.

Request:
```json
{
  "sessionID": "session-uuid-here",
  "file_id": "file-uuid-here",
  "recipient_id": 456,
  "is_group": false,
  "file_name": "image.jpg",
  "file_type": "image/jpeg"
}
```

The server will respond by sending a `new_message` event with the file information.

### Contact Management

#### Get Contacts

**Event**: `get_contacts`  
**Direction**: Client → Server  
**Description**: Get list of all contacts.

Request:
```json
{
  "sessionID": "session-uuid-here"
}
```

**Event**: `contacts`  
**Direction**: Server → Client  
**Description**: List of all contacts.

Response:
```json
{
  "contacts": [
    {
      "user_id": 456,
      "username": "janedoe",
      "status": "FRIEND",
      "is_online": true,
      "last_seen": "2023-01-01T12:00:00Z",
      "streak": 3,
      "continue_streak": true
    },
    // More contacts...
  ]
}
```

#### Add Contact

**Event**: `add_contact`  
**Direction**: Client → Server  
**Description**: Add a new contact by username.

Request:
```json
{
  "sessionID": "session-uuid-here",
  "contact_username": "newcontact"
}
```

**Event**: `contact_added`  
**Direction**: Server → Client  
**Description**: Confirmation that contact was added.

Response to requester:
```json
{
  "user_id": 789,
  "username": "newcontact",
  "status": "NEW"
}
```

**Event**: `contact_request`  
**Direction**: Server → Client  
**Description**: Notification to added user about request.

Response to added contact:
```json
{
  "user_id": 123,
  "username": "johndoe"
}
```

#### Accept Contact

**Event**: `accept_contact`  
**Direction**: Client → Server  
**Description**: Accept a contact request.

Request:
```json
{
  "sessionID": "session-uuid-here",
  "contact_id": 123
}
```

**Event**: `contact_accepted`  
**Direction**: Server → Client  
**Description**: Notification about accepted request.

Response to both users:
```json
{
  "user_id": 123,  // The other user's ID
  "username": "johndoe",  // The other user's name
  "status": "FRIEND"
}
```

#### Reject Contact

**Event**: `reject_contact`  
**Direction**: Client → Server  
**Description**: Reject a contact request.

Request:
```json
{
  "sessionID": "session-uuid-here",
  "contact_id": 123
}
```

**Event**: `contact_rejected`  
**Direction**: Server → Client  
**Description**: Notification about rejected request.

Response to both users:
```json
{
  "user_id": 123  // The other user's ID
}
```

#### Block Contact

**Event**: `block_contact`  
**Direction**: Client → Server  
**Description**: Block an existing contact.

Request:
```json
{
  "sessionID": "session-uuid-here",
  "contact_id": 123
}
```

**Event**: `contact_blocked`  
**Direction**: Server → Client  
**Description**: Confirmation that contact was blocked.

Response:
```json
{
  "user_id": 123
}
```

### Error Handling

**Event**: `error`  
**Direction**: Server → Client  
**Description**: Any error that occurs during processing.

```json
{
  "message": "Error message explaining what went wrong"
}
```

## Security Features

### Authentication
- Session-based authentication with token verification
- Session expiry and automatic cleanup
- Rate limiting to prevent abuse
- Max 3 concurrent sessions per user

### Data Validation
- All endpoints validate input parameters
- File type and size validation
- Rate limiting for high-frequency events

### Privacy
- Message encryption support via `encrypted_content` field
- Proper message deletion (soft delete)
- User status visibility control

## Type Definitions

### Message Types
- `text`: Standard text message
- `image`: Image file
- `video`: Video file
- `audio`: Audio file
- `file`: Generic file

### Contact Status Enum
- `NEW`: Contact request pending
- `FRIEND`: Accepted contact
- `BLOCKED`: Blocked contact

## Implementation Notes

1. All timestamps are in ISO 8601 format when transmitted as strings
2. User IDs and chat IDs are integers
3. Message IDs, session IDs, and file IDs are UUIDs stored as strings
4. File content for `image`, `video`, `audio`, and `file` types is stored as a JSON string with metadata
5. Rate limiting is applied to high-traffic endpoints
6. WebSocket rooms are used to manage message broadcasting
7. Redis is used for rate limiting when available, with in-memory fallback