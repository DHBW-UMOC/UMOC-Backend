# UMOC-Backend API Documentation

# DTOs
GroupMember DTO -> /getChats
```ts
export interface GroupMember {
  user_id: string; // UUID
  name: string;
  profile_picture: string; // URL
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
  status: 'FRIEND' | 'BLOCKED' | 'NEW' | 'TIMEOUT' | 'LASTWORDS';
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
    "status": "FRIEND | BLOCKED | NEW | TIMEOUT | LASTWORDS"
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**: `{"success": "Contact status changed successfully"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "'contact_id' is required"}`
    - **Content**: `{"error": "'status' is required"}`
  - **Code**: 500
    - **Content**: `{"error": "Failed to change contact status"}`

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
              "picture_url": "Link to JPG"
            },
            {
              "is_group": false,
              "contact_id": "00000000-0000-0000-0000-000000000000",
              "name": "String",
              "status": "FRIEND | BLOCKED | NEW | TIMEOUT | LASTWORDS",
              "streak": "int | null",
              "picture_url": "Link to JPG"
            },
            {
              "is_group": true,
              "group_id": "00000000-0000-0000-0000-000000000000",
              "name": "String",
              "picture_url": "Link to JPG",
              "admin_user_id": "00000000-0000-0000-0000-000000000000",
              "create_at": "Link to JPG"
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
