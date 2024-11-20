# API Endpoints
## 1. Register a User
Endpoint: ```/register```

Method: ```POST```

Parameters:

- ```username``` (string) ```"user1"```: The username for registration.
- ```password``` (string) ```"password1"```: The password for registration.

Response:
```json
{
    "success": "User registered successfully"
}
```
```json
{
    "error": "No username provided for register"
}
```

## 2. Login a User
Endpoint: ```/login```

Method: ```POST```

Parameters:

- ```username``` (string) ```"user1"```: The username of the user.
- ```password``` (string) ```"password1"```: The password of the user.
- ```public_key``` (string, Optional, Not used) ```"public_key1"```: The public key of the user.

Response:
```json
{
    "success": "User logged in, session ID created"
}
```
```json
{
    "error": "No username provided for login"
}
```

## 3. Logout a User
Endpoint: ```/logout```

Method: ```POST```

Parameters:

- ```sessionID``` (string) ```"00000000-0000-0000-0000-000000000001"```: The session ID of the user.

Response:
```json
{
    "success": "User logged out successfully"
}
```
```json
{
    "error": "No sessionID provided for logout"
}
```

## 4. Add a Contact
Endpoint: ```/addContact```

Method: ```POST```

Parameters:

- ```sessionID``` (string(uuid)) ```"00000000-0000-0000-1111-000000000001"```: The session ID of the user.
- ```contactID``` (string(uuid)) ```"00000000-0000-0000-0000-000000000002"```: The contact's username.

Response:
```json
{
    "success": "Contact added successfully"
}
```
```json
{
    "error": "No sessionID provided for addContact"
}
```

## 5. Change Contact Status
Endpoint: ```/changeContact```

Method: ```POST```

Parameters:

- ```sessionID``` (string) ```"00000000-0000-0000-1111-000000000001"```: The session ID of the user.
- ```contact``` (string) ```"00000000-0000-0000-0000-000000000002"```: The contact's username.

Response:
```json
{
    "success": "Contact status changed successfully"
}
```
```json
{
    "error": "No sessionID provided for changeContact"
}
```

## 6. Get Contacts
Endpoint: ```/getContacts```

Method: ```GET```

Parameters:

- ```sessionID``` (string) ```"00000000-0000-0000-1111-000000000001"```: The session ID of the user.

Response:
```json
{
	"contacts": [
		{
			"contact_id": "00000000-0000-0000-0000-000000000002",
			"name": "user2",
			"url": "https://static.spektrum.de/fm/912/f2000/205090.jpg"
		},
		{
			"contact_id": "00000000-0000-0000-0000-000000000003",
			"name": "user3",
			"url": "https://static.spektrum.de/fm/912/f2000/205090.jpg"
		}
	]
}
```
```json
{
    "error": "No sessionID provided for getContacts"
}
```

## 7. Get Contact Messages
Endpoint: ```/getContactMessages```

Method: ```GET```

Parameters:

- ```sessionID``` (string) ```"00000000-0000-0000-1111-000000000001"```: The session ID of the user.
- ```contactID``` (string) ```"00000000-0000-0000-0000-000000000002"```: The contact's username.

Response:
```json
{
	"messages": [
		{
			"content": "Hello, this is a test message.",
			"send_at": "Wed, 20 Nov 2024 15:43:29 GMT",
			"sender_user_id": "00000000-0000-0000-0000-000000000001"
		}
	]
}
```
```json
{
    "error": "No sessionID provided for getContactMessages"
}
```

## 8. Save Message
Endpoint: ```/saveMessage```

Method: ```POST```

Parameters:

```json
{
    "sessionID": "00000000-0000-0000-1111-000000000001",
    "recipientID": "00000000-0000-0000-0000-000000000002",
    "content": "Hello, this is a test message."
}
```

Response:
```json
{
    "success": "Message saved successfully"
}
```
```json
{
    "error": "No sessionID provided for saveMessage"
}
```

