## Cahngelog - Max - 11.06.2025
### Neue Endpunkte
- **POST `deleteMessage`** – Löscht eine Nachricht in einem Chat.
  - **Parameter**:
    - `message_id`: ID der zu löschenden Nachricht.
  - **Beispiel-Request**:
    ```json
    {
      "message_id": "00000000-0000-0000-0000-000000000001"
    }
    ```
  - **Beispiel-Antwort (200)**:
    ```json
    {
      "success": "Message deleted successfully"
    }
    ```


## Changelog - Max - 04.06.2025

### API Changes
- **GET `/getItemList`**:
  - Returns a list of items that exist.
  - Example response:
    ```json
    {
      "items": [
        {
          "name": "Lightmode",
          "price": 5
        },
        {
          "name": "Alt_Chat",
          "price": 5
        },
        {
          "name": "Ad",
          "price": 2
        }
      ]
    }
    ```

  - **GET `/getInventory`**:
    - Returns the inventory of the user.
    - The inventory is a list of items that the user has bought.
    - Example response:
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
    
    - **GET `/getActiveItems`**:
      - Returns a list of items that are currently active for the user.
      - Example response:
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
    
- **POST `/buyItem`**:
- Allows users to buy an item from the list of available items.
  - Requires `item_name` parameter in the request body.
  - Example request:
    ```json
    {
      "item_name": "Lightmode",
      "amount": 1
    }
    ```
    
- **POST `/useItem`**:
  - Allows users to use an item from their inventory.
  - Requires `item_name` parameter in the request body.
  - Example request:
    ```json
    {
      "item_name": "Lightmode",
      "to_user_id": "00000000-0000-0000-0000-000000000001"
    }
    ```

- Websocket `item_used`:
  - Comes, when a user uses an item on you.
  - Example response:
    ```json
    {
      "item_name": "Lightmode",
      "from_user_id": "00000000-0000-0000-0000-000000000001",
      "send_by_user_id": "00000000-0000-0000-0000-000000000002",
      "active_until": "2023-10-01T12:00:00.000000Z"
    }
    ```




## Changelog - Pascal - 04.06.2025

### Enhanced Contact Status System

**actions** you can **USE**! -> this is what you **SEND**! a user **cannot have these as status!!**:
- `friend`: Add as friend or accept friend request
- `blocked`: Block the contact
- `unblock`: Unblock the contact
- `unfirend`: Unfriend the contact

**states** you **cannot** use -> these are returned as a state -> DO NOT USE THESE:
  - `pending_friend`: Friend request awaiting acceptance
  - `last_words`: User can send one final message before being fully blocked
  - `blocked`: User has blocked another user
  - `fblocked`: You are blocked by a other user that you havent blocked
  - `new`: Newly added contact
  - `timeout`: Contact is in timeout
  - `ntcon`: Not connected

### API Changes
- **POST `/changeContact`**:
  - **Limited manual status changes** to `friend`, `block`, and `unblock` only
  - System-controlled statuses (`new`, `last_words`, `timeout`, etc.) cannot be set manually
  - More specific success responses based on action:
    - `{"success": "The user has been blocked"}`
    - `{"success": "The user has been unblocked"}`
    - `{"success": "You are now friends!"}`
    - `{"success": "Friend request sent!"}`
  - Enhanced validation with descriptive error messages
  - Two-way status synchronization between users
  - Smart status transitions:
    - Blocking a user gives them `last_words` status to send one final message
    - After sending message in `last_words` status, user moves to `fblocked`
    - Friend requests follow two-step confirmation process

## Changelog - Max - 04.06.2025
- send_char Websocket:
  - Der Websocket "send_char" wurde mit username erweitert.
  - Beispiel:
  ```json
  {
      'sender_id': "00000000-0000-0000-0000-000000000000",
      'sender_username': "MaxMustermann",
      'char': "H",
      'is_group': True | False,
      'recipient_id': "00000000-0000-0000-0000-000000000000"
  }
  ```



## Changelog - Max - 26.05.2025 (2)
### Get Chats
- Es wurde das Attribut `last_message_timestamp` hinzugefügt, welches den Zeitstempel der letzten Nachricht in einem Chat enthält.
  Falls es keine las message gibt wird bei Gruppen das beitritsdatum verwendet und bei Einzelchats der einen defaul timestamp.

### Websocket "send_char"
- Der Websocket "send_char" braucht jetzt nicht mehr das "is_group" Attriibute.
Beispiel:
```js
socket.emit("send_char", {
  recipient_id: "00000000-0000-0000-0000-000000000000",
  char: "H"
});
```

## Chnagelog - Pascal - 20.05.2025

### Neue Endpoints
- changeProfile

## Endpoint: `/changeProfile`

**Method**: `POST`  
**Authentication**: JWT token required  
**Content-Type**: `application/json` or URL parameters

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | Type of profile change: `"picture"`, `"name"`, or `"password"` |
| `new_value` | string | Yes | New value for the selected profile attribute |
| `old_password` | string | Only for password changes | Current password required for verification |

### Response

**Success Response (200 OK)**
```json
{
  "success": "Profile [action] updated successfully"
}
```

**Error Responses (400 Bad Request)**
```json
{"error": "'action' is required"}
{"error": "'action' must be either 'picture', 'name' or 'password'"}
{"error": "'new_value' is required"}
{"error": "'old_password' is required"} // For password changes
```

### Example Usage

#### Change Profile Picture
```http
POST /api/changeProfile
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "action": "picture",
  "new_value": "https://example.com/new-profile-image.jpg"
}
```

#### Change Username
```http
POST /api/changeProfile
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "action": "name",
  "new_value": "NewUsername123"
}
```

#### Change Password
```http
POST /api/changeProfile
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "action": "password",
  "old_password": "currentPassword123",
  "new_value": "newSecurePassword456"
}
```



## Changelog - Max - 16.05.2025

### Neue Websockets
#### Sending Websockets
- connect
- disconnect
- send_char

#### Receiving Websockets
- connect
- disconnect
- receve_char
- new_message
- chat_change
  - leave_group
  - change_group
  - add_member
  - remove_member
  - create_group
  - delete_group

Diese Events werden an alle Clients gesendet, die betroffen sind.


## Changelog – Pascal - 15.05.2025

### Neue Endpunkte

- **GET `/getAllUsers`** – Sucht nach Benutzern anhand eines Suchbegriffs.
  - Authentifizierung per JWT erforderlich.
  - Query-Parameter: `searchBy` (Suchbegriff, z.B. Teil des Benutzernamens).
  - Gibt eine Liste von Benutzern zurück, die dem Suchbegriff entsprechen.
  - Fehler, falls kein Suchbegriff angegeben oder der User nicht gefunden wird.

  **Beispiel-Request:**
  ```
  GET /getAllUsers?searchBy=alice
  Authorization: Bearer <JWT>
  ```

  **Beispiel-Antwort (200):**
  ```json
  {
    "users": [
      {
        "user_id": "123",
        "username": "alice",
        "profile_picture": "https://example.com/profile/alice.jpg"
      }
    ]
  }
  ```

### Geänderte Endpunkte
- **GET `/getChats`**:
  - Die Antwort enthält jetzt zusätzlich das Feld `am_admin`, das angibt, ob der aktuelle Benutzer Admin der Gruppe ist.

- **GET `/changeGroup`**:
  - Der Endpoint kann ab sofort nutzern den Admin Zugang entziehen, durch den Parameter `action` mit dem Wert `deadmin` kann dieser Vorgang durchgeführt werden.



## Changelog – Max - 07.05.2025

### Neue Endpunkte
- **POST `/leaveGroup`** – Eine Gruppe verlassen.
- **POST `/getOwnProfile`** – eigenen Profil zurückgeben.

### Geänderte Endpunkte
- **POST `/getChatMessages `**:
-  Rückgabe enthält memebers anstatt group_admin_id.

### Gelöschte Endpunkte
- **POST `/getGroupMembers`**

## Changelog – Max - 29.04.2025

### Neue Endpunkte
- **POST `/createGroup`** – Erstellt neue Gruppen.
- **POST `/deleteGroup`** – Löscht Gruppen.
- **POST `/changeGroup`** – Ändert Gruppendaten (Name, Bild, Admin).
- **POST `/addMember`** – Fügt Mitglieder hinzu.
- **POST `/removeMember`** – Entfernt Mitglieder.
- **GET `/getGroupMembers`** – Holt alle Mitglieder einer Gruppe.

### Geänderte Endpunkte
- **`GET /getContacts` → `GET /getChats`**:
  - Name des Endpunkts geändert.
  - Rückgabe enthält jetzt zusätzlich Gruppenchats mit `"is_group": true`.
  - Rückgabe für Kontakte ergänzt um `picture_url` (vorher `url`).
  - JSON-Property `contacts` → `chats`.

- **`GET /getContactMessages` → `GET /getChatMessages`**:
  - Endpunkt umbenannt.
  - Query-Param `contact_id` → `chat_id` (kann jetzt auch Gruppen-ID sein).
  - Kann jetzt auch Gruppennachrichten zurückgeben.

### Breaking Changes
- Alle Clients müssen folgende Änderungen übernehmen:
  - Statt `/getContacts` jetzt `/getChats` verwenden.
  - JSON-Keys: `contacts` → `chats`, `url` → `picture_url`.
  - Nachrichten-Endpunkt umbenannt + `chat_id` statt `contact_id`.
