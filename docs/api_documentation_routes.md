# UMOC-Backend API Documentation

# DTOs
GroupMember DTO -> /getChats
```ts
export interface GroupMember {
  user_id: string; // UUID
  name: string;
  picture_url: string; // URL
  role: 'admin' | 'member';
}
```

Group DTO -> /getChats
```ts
export interface Group {
  is_group: true;
  contact_id: string; // UUID
  name: string;
  picture_url: string; // URL
  created_at: string; // ISO8601 date string
  members: GroupMember[];
}
```

Contact DTO -> /getChats
```ts
export interface Contact {
  is_group: false;
  contact_id: string; // UUID
  name: string;
  picture_url: string; // URL
  status: 'FRIEND' | 'BLOCK' | 'NEW' | 'TIMEOUT' | 'LASTWORDS';
  streak: number | null;
}
```

---

This document outlines all available endpoints for the UMOC-Backend API.

## Base URL

All endpoints are relative to the base URL of the API server.

## Authentication Endpoints

### Register User

Register a new user account.

- **URL**: `/register`
- **Method**: `POST`
- **URL Parameters**:
 ```json
  {
    "username": "user_name",
    "password": "user_password",
    "profile_picture": "https://profile_picture_url.jpeg"
  }
  ```
- **Success Response**:
  - **Code**: 201
  - **Content**: `{"success": "User registered successfully"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "'username' is required"}`
    - **Content**: `{"error": "'password' is required"}`
    - **Content**: `{"error": "Username can only contain letters, numbers, dots (.) and underscores (_)"}`
    - **Content**: `{"error": "Password must be between 4 and 100 characters long"}`
    - **Content**: `{"error": "Username must be between 3 and 25 characters long"}`
  - **Code**: 409
    - **Content**: `{"error": "Username already exists"}`
  - **Code**: 500
    - **Content**: `{"error": "An unexpected error occurred during registration"}`

### Login

Authenticate a user and receive a JWT access token.

- **URL**: `/login`
- **Method**: `GET`
- **URL Parameters**:
```json
  {
    "username": "user_name",
    "password": "user_password"
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "access_token": "jwt_access_token",
      "expires_in": 86400
    }
    ```
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "'username' is required"}`
    - **Content**: `{"error": "'password' is required"}`
  - **Code**: 401
    - **Content**: `{"error": "Invalid credentials"}`
  - **Code**: 500
    - **Content**: `{"error": "An unexpected error occurred during login"}`

### Logout

End a user's session.

- **URL**: `/logout`
- **Method**: `POST`
- **Headers**:
  - `Authorization`: Bearer `<JWT access token>`
- **Success Response**:
  - **Code**: 200
  - **Content**: `{"success": "User logged out successfully"}`
- **Error Response**:
  - **Code**: 500
    - **Content**: `{"error": "An unexpected error occurred during logout"}`

## Contact Management Endpoints

### Add Contact

Add a new contact to a user's contact list.

- **URL**: `/addContact`
- **Method**: `POST`
- **Headers**:
  - `Authorization`: Bearer `<JWT access token>`
- **Request Body**:
  ```json
  {
    "contact_name": "contact_name"
  }
  ```
- **Success Response**:
  - **Code**: 201
  - **Content**: `{"success": "Contact was added successfully"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "'contact_name' is required"}`
    - **Content**: `{"error": "Contact already exists"}`
    - **Content**: `{"error": "Contact not found.", "suggestions": ["contact_name", "contact_name2"]}`
    - **Content**: `{"error": "Contact not found."}`

### Change Contact Status

Change the status of a contact.

- **URL**: `/changeContact`
- **Method**: `POST`
- **Headers**:
  - `Authorization`: Bearer `<JWT access token>`
- **Request Body**:
  ```json
  {
    "contact_id": "00000000-0000-0000-0000-000000000000",
    "status": "friend | block | unblock"
  }
  ```
- **Status Description**:
  - `friend`: Add as friend or accept friend request  - `block`: Block the contact
  - `unblock`: Unblock the contact
  - `unfirend`: Unfriend the contact
  - System-controlled statuses (cannot be set manually):
    - `new`: Newly added contact
    - `last_words`: Contact can send one final message before being fully blocked
    - `timeout`: Contact is in timeout
    - `pending_friend`: Friend request is pending
    - `fblocked`: Fully blocked (after last words)
    - `ntcon`: Not connected

- **Success Response**:
  - **Code**: 200    - **Content**: `{"success": "The user has been blocked"}`
    - **Content**: `{"success": "The user has been unblocked"}`
    - **Content**: `{"success": "You are now friends!"}`
    - **Content**: `{"success": "Friend request sent!"}`
    - **Content**: `{"success": true}`

- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "'contact_id' is required"}`
    - **Content**: `{"error": "'status' is required"}`
    - **Content**: `{"error": "Invalid status. Valid options: friend, unfriend, pending_friend, last_words, block, fblocked, unblock, new, timeout, ntcon"}`
    - **Content**: `{"error": "Status 'new' cannot be set manually. It is controlled by the system."}`
    - **Content**: `{"error": "Status 'pending_friend' cannot be set manually. Allowed statuses: friend, block, unblock"}`
    - **Content**: `{"error": "Contact not found"}`
    - **Content**: `{"error": "The user cant be unblocked because of there is another rule preventing it"}`
    - **Content**: `{"error": "The user cant be added as a friend because of there is another rule preventing it"}`
    - **Content**: `{"error": "The user cant be unfriended because of there is another rule preventing it"}`
  - **Code**: 500
    - **Content**: `{"error": "Failed to change contact status"}`
    - **Content**: `{"error": "Database error: str(e)"}`

### Get Contacts

Retrieve all contacts for the authenticated user.

- **URL**: `/getChats`
- **Method**: `GET`
- **Headers**:
  - `Authorization`: Bearer `<JWT access token>`
- **Success Response**:
  - **Code**: 200
    - **Content**:
        ```json
        {
          "chats": [
            {
              "is_group": false,
              "contact_id": "00000000-0000-0000-0000-000000000000",
              "name": "String",
              "status": "FRIEND | BLOCKED | NEW | TIMEOUT | LASTWORDS",
              "streak": "int | null",
              "picture_url": "Link to JPG",
              "last_message_timestamp": "2023-10-01T12:00:00.000000Z"
            },
            {
              "is_group": false,
              "contact_id": "00000000-0000-0000-0000-000000000000",
              "name": "String",
              "status": "FRIEND | BLOCKED | NEW | TIMEOUT | LASTWORDS",
              "streak": "int | null",
              "picture_url": "Link to JPG",
              "last_message_timestamp": "2023-10-01T12:00:00.000000Z"
            },
            {
              "is_group": true,
              "group_id": "00000000-0000-0000-0000-000000000000",
              "name": "String",
              "picture_url": "Link to JPG",
              "admin_user_id": "00000000-0000-0000-0000-000000000000",
              "create_at": "Link to JPG",
              "last_message_timestamp": "2023-10-01T12:00:00.000000Z",
              "members": [
                {
                  "user_id": "00000000-0000-0000-0000-000000000001",
                  "name": "String",
                  "picture_url": "Link to JPG",
                  "role": "admin | member"
                },
                {
                  "user_id": "00000000-0000-0000-0000-000000000002",
                  "name": "String",
                  "picture_url": "Link to JPG",
                  "role": "admin | member"
                }
              ]
            }
          ]
      }
      ```
- **Error Response**:
  - **Code**: 500
    - **Content**: `{"error": "Failed to retrieve contacts"}`

## Messaging Endpoints

### Get Contact Messages

Retrieve all messages between the authenticated user and a specific contact.

- **URL**: `/getChatMessages`
- **Method**: `GET`
- **Headers**:
  - `Authorization`: Bearer `<JWT access token>`
- **Query Parameters**:
  - `chat_id`: ID of the contact
  - `page`: Page number for pagination (optional; Page=20 messages); Bei None bekommt man alle Messages.
- **Success Response**:
  - **Code**: 200
  - **Content**: 
    ```json
    {
      "messages":[
          {
            "content":"String",
            "message_id":"00000000-0000-0000-0000-000000000000",
            "recipient_id":"00000000-0000-0000-0000-000000000000",
            "sender_user_id":"00000000-0000-0000-0000-000000000000",
            "sender_username":"String",
            "timestamp":"0000-00-00T00:00:00.000000",
            "type":"TEXT | IMAGE | ITEM | LOCATION | AUDIO | VIDEO"
          },
          {
            "content":"String",
            "message_id":"00000000-0000-0000-0000-000000000000",
            "recipient_id":"00000000-0000-0000-0000-000000000000",
            "sender_user_id":"00000000-0000-0000-0000-000000000000",
            "sender_username":"String",
            "timestamp":"0000-00-00T00:00:00.000000",
            "type":"TEXT | IMAGE | ITEM | LOCATION | AUDIO | VIDEO"
          }
      ]
    }
    ```

- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "'chat_id' is required"}`
  - **Code**: 500
    - **Content**: `{"error": "Failed to retrieve messages"}`

### Save Message

Save a new message.

- **URL**: `/saveMessage`
- **Method**: `POST`
- **Headers**:
  - `Authorization`: Bearer `<JWT access token>`
- **Request Body**:
  ```json
  {
    "recipient_id": "00000000-0000-0000-0000-000000000000",
    "content": "string"
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**: `{"success": "Message saved successfully", "message_id": "message_id"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "'recipient_id' is required"}`
    - **Content**: `{"error": "'content' is required"}`
  - **Code**: 500
    - **Content**: `{"error": "Failed to save message"}`

### Get Own Profile
- **URL**: `/getOwnProfile`
- **Method**: `GET`
- **Headers**:
  - `Authorization`: Bearer `<JWT access token>`

- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "user_id": "00000000-0000-0000-0000-000000000000",
      "username": "String",
      "profile_picture": "https://profile_picture_url.jpeg"
    }
    ```
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "User not found"}`


## Group Endpoints

### Create Group
Create a new group.
- **URL**: `/createGroup`
- **Method**: `POST`
- **Headers**:
  - `Authorization`: Bearer `<JWT access token>`
- **Request Body**:
  ```json
  {
    "group_name": "group_name",
    "group_pic": "https://group_pic_url.jpeg",
    "group_members": ["00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000"]
  }
  ```
- **Success Response**:
- **Code**: 201
  - **Content**: `{"success": "Group created successfully", "group_id": "00000000-0000-0000-0000-000000000000"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "'group_name' is required"}`
    - **Content**: `{"error": "Group name already exists"}`
    - **Content**: `{"error": "'group_pic' is required"}`
    - **Content**: `{"error": "'group_members' are required"}`
    - **Content**: `{"error": "Group members not found."}`
    - **Content**: `{"error": "Group members must be a list"}`
    - **Content**: `{"error": "Group name must be between 3 and 25 characters long"}`
    - **Content**: `{"error": "Group can have at most 50 members"}`
    - **Content**: `{"error": "Group must have at least 2 members"}`
    - **Content**: `"error": "Database error: str(e)"`

### Delete Group
Delete a group.
- **URL**: `/deleteGroup`
- **Method**: `POST`
- **Headers**:
  - `Authorization`: Bearer `<JWT access token>`
- **Request Body**:
  ```json
  {
    "group_id": "00000000-0000-0000-0000-000000000000"
  }
  ```
- **Success Response**:
- **Code**: 201
  - **Content**: `{"success": "Group deleted successfully"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "'group_id' is required"}`
    - **Content**: `{"error": "User not found"}`
    - **Content**: `{"error": "Group not found"}`
    - **Content**: `{"error": "User is not admin of the group"}`
    - **Content**: `{"error": "Database error: str(e)"}`

### Change Group
Change a group. Ethere the Name, Group picture or who the admin is.
- **URL**: `/changeGroup`
- **Method**: `POST`
- **Headers**:
  - `Authorization`: Bearer `<JWT access token>`
- **Request Body**:
  ```json
  {
    "action": "name | picture | admin",
    "group_id": "00000000-0000-0000-0000-000000000000",
    "new_value": "new_name | new_picture_url | new_admin_id"
  }
  ```
- **Success Response**:
- **Code**: 201
  - **Content**: `{"success": "Group updated successfully"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "'new_value' is required"}`
    - **Content**: `{"error": "'group_id' is required"}`
    - **Content**: `{"error": "'action' is required. Valid values: name, picture, admin"}`
    - **Content**: `{"error": "User is not admin of the group"}`
    - **Content**: `{"error": "Group not found"}`
    - **Content**: `{"error": "User not found"}`

### Add Member
Add Member to a Group.
- **URL**: `/addMember`
- **Method**: `POST`
- **Headers**:
  - `Authorization`: Bearer `<JWT access token>`
- **Request Body**:
  ```json
  {
    "group_id": "00000000-0000-0000-0000-000000000000",
    "new_member_id": "00000000-0000-0000-0000-000000000000"
  }
  ```
- **Success Response**:
- **Code**: 201
  - **Content**: `{"success": "Group updated successfully"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "'group_id' is required"}`
    - **Content**: `{"error": "'new_member_id' is required"}`
    - **Content**: `{"error": "'new_member_id' is required"}`
    - **Content**: `{"error": "User not found"}`
    - **Content**: `{"error": "New member not found"}`
    - **Content**: `{"error": "Group not found"}`
  - **Code**: 403
    - **Content**: `{"error": "User is not admin of the group"}`
  - **Code**: 409
    - **Content**: `{"error": "New member is already in the group"}`

### Remove member
Remove a Member from a Group.
- **URL**: `/removeMember`
- **Method**: `POST`
- **Headers**:
  - `Authorization`: Bearer `<JWT access token>`
- **Request Body**:
  ```json
  {
    "group_id": "00000000-0000-0000-0000-000000000000",
    "new_member_id": "00000000-0000-0000-0000-000000000000"
  }
  ```
- **Success Response**:
- **Code**: 201
  - **Content**: `{"success": "Group created successfully", "group_id": "group_id"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "'group_id' is required"}`
    - **Content**: `{"error": "'member_id' is required"}`
    - **Content**: `{"error": "User not found"}`
    - **Content**: `{"error": "Member not found"}`
    - **Content**: `{"error": "Group not found"}`
    - **Content**: `{"error": "User is not admin of the group"}`
    - **Content**: `{"error": "Member is not in the group"}`

### Leave Group
Get all Members of a group
- **URL**: `/leaveGroup`
- **Method**: `POST`
- **Headers**:
  - `Authorization`: Bearer `<JWT access token>`
- **Request Body**:
  ```json
  {
    "group_id": "00000000-0000-0000-0000-000000000000"
  }
  ```
- **Success Response**:
  - **Code**: 201
    - **Content**: `{"success": "User left the group successfully"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "User not found"}`
    - **Content**: `{"error": "Group not found"}`
    - **Content**: `{"error": "'group_id' is required"}`
    - **Content**: `{"error": "User is not a member of the group"}`


### Get Item List
Get all Items that exist.
- **URL**: `/getItemList`
- **Method**: `GET`
- **Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "items": [
        {
          "name": "String",
          "price": 10
        },
        {
          "name": "String",
          "price": 5
        }
      ]
    }
    ```
    
### Get Inventory
Get all Items that the user has.
- **URL**: `/getInventory`
- **Method**: `GET`
- Response:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "items": [
        {
          "name": "String",
          "amount": 10
        },
        {
          "name": "String",
          "amount": 5
        }
      ]
    }
    ```
    
### Get Active Items
Get all Items that effect the user.
- **URL**: `/getActiveItems`
- **Method**: `GET`
- Response:
  - **Code**: 200
  - **Content**:
```json
{
  "items": [
    {
        "item": "String",
        "user_id": "00000000-0000-0000-0000-000000000000",
        "send_by_user_id": "00000000-0000-0000-0000-000000000001",
        "active_until": "2023-10-01T12:00:00.000000Z"
    },
    {
        "item": "String",
        "user_id": "00000000-0000-0000-0000-000000000002",
        "send_by_user_id": "00000000-0000-0000-0000-000000000003",
        "active_until": "2023-10-01T12:00:00.000000Z"
    }
  ]
}
```

### Use Item
Use an Item from the Inventory.
- **URL**: `/useItem`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "item_name": "String",
    "to_user_id": "00000000-0000-0000-0000-000000000000"
  }
  ```
  
### Buy Item
Buy an Item from the Item List.
- **URL**: `/buyItem`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "item_name": "String",
    "amount": 1
  }
  ```
- **Success Response**:
- **Code**: 201
  - **Content**: `{"success": "Item bought successfully"}`


## Utility Endpoints

### API Root

Simple test endpoint to verify API is running.

- **URL**: `/`
- **Method**: `GET`
- **Success Response**:
  - **Code**: 200
  - **Content**: `"UMOC Backend API"`

### Debug Contacts

Debug endpoint to retrieve detailed contact information.

- **URL**: `/debugContacts`
- **Method**: `GET`
- **Headers**:
  - `Authorization`: Bearer `<JWT access token>`
- **Success Response**:
  - **Code**: 200
  - **Content**: Detailed contact debug information
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "User not found"}`



## WebSocket Interface

### Connect
Zum verbinden mit dem WebSocket-Server wird ein JWT-Token benötigt. 
Der Token muss als Query-Parameter `token` übergeben werden.
Beispiel: 
```html
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<srcipt>
  const SERVER_URL = "http://localhost:5000";
  const TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmV......"
  
  const socket = io(SERVER_URL, {
    query: { token: TOKEN } 
  });
  
  socket.on("connect", () => {
    console.log("Connected");
  });
</srcipt>
```

### Disconnect
Manuel muss man sich nicht trennen. Falls die Verbindung getrennt wird, wird der Client automatisch disconnected.
```js
socket.on("disconnect", () => {
  console.log("Disconnected");
});
```

### Send Char (Typing)
event: `send_char`
- **Client Payload**:
```json
{
  "sender_id": "00000000-0000-0000-0000-000000000000",
  "sender_username": "String",
  "char": "H" / "<DEL>",
  "is_group": false | true,
  "recipient_id": "00000000-0000-0000-0000-000000000000",
}
```
Beispiel:
```js
socket.emit("send_char", {
  recipient_id: "00000000-0000-0000-0000-000000000000",
  char: "H"
});
```

### receving_events
Diese werden wie volgt empfangen:
```js
socket.on("receive_char", (data) => {
  console.log(data);
});
```

#### Receve Char
event: "receive_char"
- **Server Payload**:
```json
{
  "sender_id": "00000000-0000-0000-0000-000000000000",
  "char": "H" / "<DEL>",
  "is_group": false | true,
  "recipient_id": "00000000-0000-0000-0000-000000000000"
}
```

#### New Message
event: "new_message"
- **Server Payload**:
```json
{
  "message_id": "00000000-0000-0000-0000-000000000000",
  "sender_id": "00000000-0000-0000-0000-000000000000",
  "content": "String",
  "type": "TEXT | IMAGE | ITEM | LOCATION | AUDIO | VIDEO",
  "timestamp": "2023-10-01T12:00:00.123456Z",
  "is_group": false | true,
  "recipient_id": "00000000-0000-0000-0000-000000000001"
}
```

##### Chat Change
event: "chat_change"
Hier sind alle Änderungen von chats in einem Websocket verbunden.
- **Server Payload**:
```json
{
  "action": "leave_group | remove_member | add_member | change_group | delete_group",
  "group_id": "00000000-0000-0000-0000-000000000000",
  "data": {
    ...
  }
}
```

###### "leave_group"
- **Server Payload**:
```json
{
  "action": "leave_group",
  "group_id": "00000000-0000-0000-0000-000000000000",
  "data": {
    "user_id": "00000000-0000-0000-0000-000000000000"
  } 
}
```

###### "remove_member"
- **Server Payload**:
```json
{
  "action": "remove_member",
  "group_id": "00000000-0000-0000-0000-000000000000",
  "data": {
    "user_id": "00000000-0000-0000-0000-000000000001",
    "by_user_id": "00000000-0000-0000-0000-000000000000"
  } 
}
```

###### "add_member"
- **Server Payload**:
```json
{
  "action": "add_member",
  "group_id": "00000000-0000-0000-0000-000000000000",
  "data": {
    "user_id": "00000000-0000-0000-0000-000000000001",
    "by_user_id": "00000000-0000-0000-0000-000000000001"
  } 
}
```

###### "create_group"
- **Server Payload**:
```json
{
  "action": "create_group",
  "group_id": "00000000-0000-0000-0000-000000000000",
  "data": {
    "group_name": "String",
    "group_pic": "https://group_pic_url.jpeg"
  } 
}
```

###### "delete_group"
- **Server Payload**:
```json
{
  "action": "delete_group",
  "group_id": "00000000-0000-0000-0000-000000000000",
  "data": {} 
}
```

###### "change_group"
- **Server Payload**:
```json
{
  "action": "change_group",
  "group_id": "00000000-0000-0000-0000-000000000000",
  "data": {
    "action": "name | picture | admin",
    "new_value": "String"
  } 
}
```


###### Item Used
event: "item_used"
- **Server Payload**:
```json
{
  "item_name": "Lightmode",
  "from_user_id": "00000000-0000-0000-0000-000000000001",
  "send_by_user_id": "00000000-0000-0000-0000-000000000002",
  "active_until": "2023-10-01T12:00:00.000000Z"
}
```
