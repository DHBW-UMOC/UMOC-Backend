## Changelog - Max - 16.05.2025

### Neue Websockets
#### Verbindung aufbauen (mit JWT)

- **Event**: `connect` (automatisch)
- **Query Param**: `token=<JWT access token>`
- **Beispiel (Client - JS)**:
  ```js
  const socket = io("http://localhost:5000", {
    query: { token: "your_jwt_token" }
  });

  socket.on("connect", () => {
    console.log("Connected!");
  });

  socket.on("user_status", (data) => {
    console.log("Status update:", data);
  });
  ```
  
#### Disconnect
Event: disconnect (automatisch bei Trennung)

Serverreaktion: Kontakte erhalten Statusmeldung

```js
{
  "user_id": "<user_id>",
  "username": "<username>",
  "status": "offline"
}
```

#### Action
Event: action

Payload:
```json
{
  "action": "<action_type>",
  "data": { ... }
}
```

#### Unterstützte Actions:

- typing

- sendMessage

Beispiel: typing
```js
socket.emit("action", {
  action: "typing",
  data: {
    recipient_id: "abc123",
    char: "a"
  }
});
```

Beispiel: sendMessage
```js
socket.emit("action", {
  action: "sendMessage",
  data: {
    recipient_id: "abc123",
    content: "Hello!",
    type: "text"
  }
});
```

#### Events vom Server:
| Event            | Beschreibung                   |
| ---------------- | ------------------------------ |
| `typing`         | Nutzer tippt Nachricht         |
| `new_message`    | Neue Nachricht empfangen       |
| `item_used`      | Item wurde verwendet           |
| `system_message` | Systemnachricht erhalten       |
| `user_status`    | Online-/Offline-Statusänderung |

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
