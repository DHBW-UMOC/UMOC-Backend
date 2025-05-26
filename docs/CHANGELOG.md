
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
