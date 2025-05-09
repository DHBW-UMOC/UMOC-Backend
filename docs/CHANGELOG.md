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
