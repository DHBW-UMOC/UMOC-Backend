# UMOC-Backend API Documentation

This document outlines all available endpoints for the UMOC-Backend API.

## Base URL

All endpoints are relative to the base URL of the API server.

## Authentication Endpoints

### Register User

Register a new user account.

- **URL**: `/register`
- **Method**: `POST`
- **URL Parameters**:
  - `username`: User's desired username
  - `password`: User's password
  - `profile_picture`: URL to the user's profile picture (optional)
- **Success Response**:
  - **Code**: 201
  - **Content**: `{"success": "User registered successfully"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "Username is required"}`
    - **Content**: `{"error": "Password is required"}`
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
  - `username`: User's username
  - `password`: User's password
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
    - **Content**: `{"error": "Username is required"}`
    - **Content**: `{"error": "Password is required"}`
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
    - **Content**: `{"error": "Contact name is required"}`
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
    "contact_id": "contact_user_id",
    "status": "new_status"
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**: `{"success": "Contact status changed successfully"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "Contact ID is required"}`
    - **Content**: `{"error": "Status is required"}`
  - **Code**: 500
    - **Content**: `{"error": "Failed to change contact status"}`

### Get Contacts

Retrieve all contacts for the authenticated user.

- **URL**: `/getContacts`
- **Method**: `GET`
- **Headers**:
  - `Authorization`: Bearer `<JWT access token>`
- **Success Response**:
  - **Code**: 200
    - **Content**:
        ```json
        {
          "contacts": [
            {
              "contact_id": "00000000-0000-0000-0000-000000000000",
              "name": "String",
              "status": "FRIEND | BLOCKED | NEW | TIMEOUT | LASTWORDS",
              "streak": "int | null",
              "url": "Link to JPG"
            },
            {
              "contact_id": "00000000-0000-0000-0000-000000000000",
              "name": "String",
              "status": "FRIEND | BLOCKED | NEW | TIMEOUT | LASTWORDS",
              "streak": "int | null",
              "url": "Link to JPG"
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

- **URL**: `/getContactMessages`
- **Method**: `GET`
- **Headers**:
  - `Authorization`: Bearer `<JWT access token>`
- **Query Parameters**:
  - `contact_id`: ID of the contact
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
    - **Content**: `{"error": "Contact ID is required"}`
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
    "recipient_id": "recipient_user_id",
    "content": "message_content",
    "is_group": false
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**: `{"success": "Message saved successfully", "message_id": "message_id"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "Recipient ID is required"}`
    - **Content**: `{"error": "Content is required"}`
  - **Code**: 500
    - **Content**: `{"error": "Failed to save message"}`

  
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
    "group_members": ["contact_id1", "contact_id2"]
  }
  ```
- **Success Response**:
- **Code**: 201
  - **Content**: `{"success": "Group created successfully", "group_id": "group_id"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "Group name is required"}`
    - **Content**: `{"error": "Group name already exists"}`
    - **Content**: `{"error": "Group picture URL is required"}`
    - **Content**: `{"error": "Group members are required"}`
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
    "group_id": "group_id"
  }
  ```
- **Success Response**:
- **Code**: 201
  - **Content**: `{"success": "Group deleted successfully"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "Group ID is required"}`
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
    "group_id": "group_id",
    "new_value": "new_name/new_picture_url/new_admin_id"
  }
  ```
- **Success Response**:
- **Code**: 201
  - **Content**: `{"success": "Group updated successfully"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "New value is required"}`
    - **Content**: `{"error": "Action is required. Valid values: name, picture, admin"}`
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
    "group_id": "group_id",
    "new_member_id": "new_member_id"
  }
  ```
- **Success Response**:
- **Code**: 201
  - **Content**: `{"success": "Group updated successfully"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "Group ID is required"}`
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
    "group_id": "group_id",
    "new_member_id": "new_member_id"
  }
  ```
- **Success Response**:
- **Code**: 201
  - **Content**: `{"success": "Group created successfully", "group_id": "group_id"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "Group ID is required"}`
    - **Content**: `{"error": "Member ID is required"}`
    - **Content**: `{"error": "User not found"}`
    - **Content**: `{"error": "Member not found"}`
    - **Content**: `{"error": "Group not found"}`
    - **Content**: `{"error": "User is not admin of the group"}`
    - **Content**: `{"error": "Member is not in the group"}`

### Get Group Members
Get all Members of a group
- **URL**: `/getGroupMembers`
- **Method**: `GET`
- **Headers**:
  - `Authorization`: Bearer `<JWT access token>`
- **Request Body**:
  ```json
  {
    "group_id": "group_id"
  }
  ```
- **Success Response**:
  - **Code**: 201
    - **Content**: 
    ```json
    {
      "members": ["member1_id", "member2_id"]
    }
    ```
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "User not found"}`
    - **Content**: `{"error": "Group not found"}`
    - **Content**: `{"error": "Group ID is required"}`


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
