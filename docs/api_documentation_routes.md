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
- **Success Response**:
  - **Code**: 201
  - **Content**: `{"success": "User registered successfully"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "Username is required"}`
    - **Content**: `{"error": "Password is required"}`
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
    "contactID": "contact_user_id"
  }
  ```
- **Success Response**:
  - **Code**: 201
  - **Content**: `{"success": "Contact was added successfully"}`
- **Error Response**:
  - **Code**: 400
    - **Content**: `{"error": "Contact ID is required"}`
  - **Code**: 500
    - **Content**: `{"error": "Failed to add contact"}`

### Change Contact Status

Change the status of a contact.

- **URL**: `/changeContact`
- **Method**: `POST`
- **Headers**:
  - `Authorization`: Bearer `<JWT access token>`
- **Request Body**:
  ```json
  {
    "contactID": "contact_user_id",
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
              "contact_id": "00000000-0000-0000-0000-000000000002",
              "name": "Max Mustermann",
              "status": "FRIEND",
              "streak": null,
              "url": "https://static.spektrum.de/fm/912/f2000/205090.jpg"
            },
            {
              "contact_id": "00000000-0000-0000-0000-000000000003",
              "name": "Angela Merkel",
              "status": "NEW",
              "streak": null,
              "url": "https://static.spektrum.de/fm/912/f2000/205090.jpg"
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
  - `contactID`: ID of the contact
- **Success Response**:
  - **Code**: 200
  - **Content**: 
    ```json
    {
      "contacts": [
        {
          "contact_id": "00000000-0000-0000-0000-000000000002",
          "name": "Max Mustermann",
          "status": "FRIEND",
          "streak": null,
          "url": "https://static.spektrum.de/fm/912/f2000/205090.jpg"
        },
        {
          "contact_id": "00000000-0000-0000-0000-000000000003",
          "name": "Angela Merkel",
          "status": "NEW",
          "streak": null,
          "url": "https://static.spektrum.de/fm/912/f2000/205090.jpg"
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
    "recipientID": "recipient_user_id",
    "content": "message_content",
    "isGroup": false
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
