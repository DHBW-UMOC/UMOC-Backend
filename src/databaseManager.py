import sqlite3
from datetime import datetime
from uuid import uuid4

# Function to get a new SQLite connection for each request
def get_connection():
    return sqlite3.connect("test.db", check_same_thread=False)

# Function to create tables if they do not already exist
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS User (
        userId TEXT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        password VARCHAR(128) NOT NULL,
        createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        sessionId TEXT DEFAULT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS "Group" (
        groupId TEXT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        adminUserId TEXT REFERENCES User(userId) ON DELETE SET NULL,
        createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS GroupAdmin (
        userId TEXT NOT NULL REFERENCES User(userId) ON DELETE CASCADE,
        groupId TEXT NOT NULL REFERENCES "Group"(groupId) ON DELETE CASCADE,
        PRIMARY KEY (userId, groupId)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS UserContact (
        userId TEXT NOT NULL REFERENCES User(userId) ON DELETE CASCADE,
        contactID TEXT NOT NULL REFERENCES User(userId) ON DELETE CASCADE,
        status VARCHAR(10) CHECK (status IN ('FRIEND', 'FAVORITE', 'BLOCKED')),
        PRIMARY KEY (userId, contactID)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS GroupContact (
        userId TEXT NOT NULL REFERENCES User(userId) ON DELETE CASCADE,
        groupId TEXT NOT NULL REFERENCES "Group"(groupId) ON DELETE CASCADE,
        PRIMARY KEY (userId, groupId)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Message (
        messageId TEXT PRIMARY KEY,
        senderUserId TEXT NOT NULL REFERENCES User(userId) ON DELETE CASCADE,
        recipientUserId TEXT REFERENCES User(userId) ON DELETE CASCADE,
        groupId TEXT REFERENCES "Group"(groupId) ON DELETE CASCADE,
        encryptedContent TEXT NOT NULL,
        sendAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS MessageStatus (
        messageId TEXT NOT NULL REFERENCES Message(messageId) ON DELETE CASCADE,
        userId TEXT NOT NULL REFERENCES User(userId) ON DELETE CASCADE,
        status VARCHAR(10) CHECK (status IN ('SENT', 'RECEIVED', 'READ')) NOT NULL,
        receivedAt TIMESTAMP DEFAULT NULL,
        readAt TIMESTAMP DEFAULT NULL,
        PRIMARY KEY (messageId, userId)
    )
    """)

    conn.commit()
    conn.close()

# Function to insert a message
def InsertMessage(senderUserId, encryptedContent, recipientUserId=None, groupId="Group1"):
    conn = get_connection()
    cursor = conn.cursor()
    messageId = str(uuid4())
    sendAt = datetime.now()

    cursor.execute("""
    INSERT INTO Message (messageId, senderUserId, recipientUserId, groupId, encryptedContent, sendAt)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (messageId, senderUserId, recipientUserId, groupId, encryptedContent, sendAt))

    conn.commit()
    conn.close()
    return messageId

# Function to retrieve messages
def getMessage(beginDate=None, endDate=None, groupId=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM Message WHERE 1=1"
    params = []

    if beginDate:
        query += " AND sendAt >= ?"
        params.append(beginDate)
    
    if endDate:
        query += " AND sendAt <= ?"
        params.append(endDate)
    
    if groupId:
        query += " AND groupId = ?"
        params.append(groupId)
    
    cursor.execute(query, tuple(params))
    messages = cursor.fetchall()
    conn.close()
    return messages

# Ensure tables are created on module load
create_tables()
