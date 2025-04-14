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
  - **Code**: 200
  - **Content**: `{"success": "User registered successfully"}`
- **Error Response**:
  - **Code**: 400
  - **Content**: `{"error": "Error message"}`

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
    - `access_token`: The JWT token to be used for authenticated requests.
    - `expires_in`: Time in seconds until the token expires.
- **Error Response**:
  - **Code**: 400
  - **Content**: `{"error": "Error message"}`

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
  - **Code**: 400
  - **Content**: `{"error": "Error message"}`

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
  - **Code**: 200
  - **Content**: `{"success": "Contact was added successfully"}`
- **Error Response**:
  - **Code**: 400
  - **Content**: `{"error": "Error message"}`

### Change Contact Status

Modify the status of an existing contact.

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
  - **Content**: `{"error": "Error message"}`

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
      "contacts": [contact_objects]
    }
    ```
- **Error Response**:
  - **Code**: 400
  - **Content**: `{"error": "Error message"}`

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
  - **Content**: Message objects
- **Error Response**:
  - **Code**: 400
  - **Content**: `{"error": "Error message"}`

### Save Message

Save a new message to a contact.

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
  - **Content**: `{"success": "Message saved successfully"}`
- **Error Response**:
  - **Code**: 400
  - **Content**: `{"error": "Error message"}`

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
  - **Content**: `{"error": "Error message"}`
