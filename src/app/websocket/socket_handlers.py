from flask import request
from flask_socketio import emit, join_room, leave_room
from datetime import datetime, timedelta
import uuid
import threading
import logging
import time
import hmac
import hashlib
import base64
import redis
import json
from flask_cors import CORS

# Use absolute imports for app modules
from app.extensions import socketio, db
from app.models.user import User, UserContact, ContactStatusEnum
from app.models.message import Message, MessageTypeEnum
from app.services.user_service import UserService
from app.services.message_service import MessageService
from app.config import Config

# Set up Redis for rate limiting if available
try:
    redis_client = redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DB,
        decode_responses=True
    )
    REDIS_AVAILABLE = True
except (redis.ConnectionError, AttributeError):
    REDIS_AVAILABLE = False
    logging.warning("Redis not available for rate limiting. Using in-memory fallback.")
    # Fallback in-memory rate limiting
    rate_limit_data = {}

# Improved user session tracking
class WebSocketManager:
    """Manages WebSocket connections and user sessions with enhanced security."""
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.connected_clients = {}  # Maps session IDs to socket IDs
        self.user_sessions = {}      # Maps user IDs to session IDs
        self.session_users = {}      # Maps session IDs to user IDs
        self.socket_sessions = {}    # Maps socket IDs to session IDs
        self.session_activity = {}   # Maps session IDs to last activity timestamp
        self.lock = threading.Lock() # Lock for thread safety
        self.session_timeout = 86400 # Session timeout in seconds (24 hours)
        self.max_sessions_per_user = 3  # Maximum number of active sessions per user
        self.token_secret = Config.SECRET_KEY
        logging.info("WebSocketManager initialized with enhanced security")
        
        # Start background task for session cleanup
        self.start_session_cleanup()
    
    def start_session_cleanup(self):
        """Start a background thread to clean up expired sessions."""
        def cleanup_task():
            while True:
                self.cleanup_expired_sessions()
                time.sleep(300)  # Check every 5 minutes
                
        cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
        cleanup_thread.start()
        logging.info("Session cleanup thread started")
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        now = time.time()
        expired_sessions = []
        
        with self.lock:
            for session_id, last_activity in self.session_activity.items():
                if now - last_activity > self.session_timeout:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                self.remove_session(session_id)
                
        if expired_sessions:
            logging.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def remove_session(self, session_id):
        """Remove a session and related data."""
        user_id = self.session_users.get(session_id)
        socket_id = self.connected_clients.get(session_id)
        
        if socket_id:
            self.socket_sessions.pop(socket_id, None)
            try:
                socketio.disconnect(socket_id)
            except Exception as e:
                logging.error(f"Error disconnecting socket: {e}")
                
        self.connected_clients.pop(session_id, None)
        self.session_users.pop(session_id, None)
        self.session_activity.pop(session_id, None)
        
        if user_id:
            # Only remove the user_sessions entry if this is the current session for the user
            if self.user_sessions.get(user_id) == session_id:
                self.user_sessions.pop(user_id, None)
                
        logging.info(f"Removed session {session_id}")
    
    def verify_token(self, session_id, token):
        """Verify the authenticity of a session token."""
        try:
            # For token-based verification when implemented
            if not session_id or not token:
                return False
                
            # Simple HMAC verification
            expected = hmac.new(
                self.token_secret.encode(),
                session_id.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected, token)
        except Exception as e:
            logging.error(f"Token verification error: {e}")
            return False
            
    def update_session_activity(self, session_id):
        """Update last activity timestamp for a session."""
        with self.lock:
            if session_id in self.session_users:
                self.session_activity[session_id] = time.time()
    
    def add_client(self, session_id, socket_id, user_id):
        """Add a new connected client with enhanced security."""
        with self.lock:
            logging.info(f"Adding client: user={user_id}, session={session_id}, socket={socket_id}")
            
            # Set initial activity timestamp
            self.session_activity[session_id] = time.time()
            
            # Check if this user already has too many active sessions
            user_sessions = []
            for s_id, u_id in self.session_users.items():
                if u_id == user_id:
                    user_sessions.append(s_id)
            
            # If max sessions reached, remove oldest session
            if len(user_sessions) >= self.max_sessions_per_user:
                oldest_session = min(user_sessions, key=lambda s: self.session_activity.get(s, 0))
                logging.info(f"User {user_id} has reached max sessions, removing oldest: {oldest_session}")
                self.remove_session(oldest_session)
            
            # Check if this user already has a different active session
            if user_id in self.user_sessions:
                old_session_id = self.user_sessions[user_id]
                if old_session_id != session_id:
                    # Get the old socket ID and disconnect it if it exists
                    old_socket_id = self.connected_clients.get(old_session_id)
                    if old_socket_id:
                        logging.info(f"Closing previous connection for user {user_id}")
                        try:
                            socketio.disconnect(old_socket_id)
                        except Exception as e:
                            logging.error(f"Error disconnecting socket: {e}")
                    
                    # Clean up old session references
                    self.connected_clients.pop(old_session_id, None)
                    self.session_users.pop(old_session_id, None)
                    self.session_activity.pop(old_session_id, None)
                    # Don't remove socket_sessions here as the disconnect handler will do it
            
            # Store the new connection
            self.connected_clients[session_id] = socket_id
            self.user_sessions[user_id] = session_id
            self.session_users[session_id] = user_id
            self.socket_sessions[socket_id] = session_id
    
    def remove_client(self, socket_id):
        """Remove a client when disconnected."""
        with self.lock:
            session_id = self.socket_sessions.get(socket_id)
            if session_id:
                user_id = self.session_users.get(session_id)
                logging.info(f"Removing client: socket={socket_id}, session={session_id}, user={user_id}")
                
                # Clean up the socket reference
                self.socket_sessions.pop(socket_id, None)
                
                # Keep the session and user mappings for potential reconnection
                # but update the connected_clients to show they're not connected
                self.connected_clients.pop(session_id, None)
                
                # We don't remove user_sessions or session_users to allow for reconnection
                # The session cleanup task will handle expired sessions
            else:
                logging.warning(f"Attempted to remove unknown socket: {socket_id}")
    
    def get_socket_id(self, session_id):
        """Get the socket ID for a session."""
        return self.connected_clients.get(session_id)
    
    def get_user_id(self, session_id):
        """Get the user ID for a session."""
        return self.session_users.get(session_id)
    
    def get_session_id(self, user_id):
        """Get the session ID for a user."""
        return self.user_sessions.get(user_id)
    
    def is_connected(self, session_id):
        """Check if a session is connected."""
        return session_id in self.connected_clients
    
    def get_active_connections_count(self):
        """Get the number of active connections."""
        return len(self.connected_clients)
    
    def get_socket_id_for_user(self, user_id):
        """Get the socket ID for a user."""
        session_id = self.get_session_id(user_id)
        if session_id:
            return self.get_socket_id(session_id)
        return None
        
    def disconnect_user(self, user_id):
        """Force disconnect a user."""
        session_id = self.get_session_id(user_id)
        if session_id:
            socket_id = self.get_socket_id(session_id)
            if socket_id:
                try:
                    socketio.disconnect(socket_id)
                    return True
                except Exception as e:
                    logging.error(f"Error disconnecting user {user_id}: {e}")
        return False
        
    def generate_session_token(self, session_id):
        """Generate a secure token for session validation."""
        return hmac.new(
            self.token_secret.encode(),
            session_id.encode(),
            hashlib.sha256
        ).hexdigest()

# Create a WebSocketManager instance
ws_manager = WebSocketManager()

# Backward compatibility - maintain the old dictionary for now
user_sids = {}  # {user_id: socket_id}
user_service = UserService()
message_service = MessageService()

# Keep track of who is typing in which chat
typing_users = {}  # {chat_room_id: {user_id: timestamp}}
typing_cleanup_interval = 5  # seconds to keep typing status active

def get_user_from_session(session_id):
    """Helper to get user from session ID with security checks"""
    if not session_id:
        return None
        
    # Update last activity timestamp
    ws_manager.update_session_activity(session_id)
    
    user_id = ws_manager.get_user_id(session_id)
    if not user_id:
        return None
        
    return User.query.get(user_id)

def check_rate_limit(key, limit=10, period=60):
    """
    Check if a rate limit has been exceeded
    Returns True if rate limit is exceeded, False otherwise
    """
    current_time = int(time.time())
    
    if REDIS_AVAILABLE:
        try:
            # Using Redis sliding window counter
            pipeline = redis_client.pipeline()
            pipeline.zadd(key, {current_time: current_time})
            pipeline.zremrangebyscore(key, 0, current_time - period)
            pipeline.zcard(key)
            pipeline.expire(key, period * 2)  # Set reasonable expiry
            results = pipeline.execute()
            count = results[2]
        except Exception as e:
            logging.error(f"Redis rate limiting error: {e}")
            # Fallback to always allow on Redis error
            return False
    else:
        # In-memory fallback implementation
        if key not in rate_limit_data:
            rate_limit_data[key] = []
            
        # Add current request timestamp
        rate_limit_data[key].append(current_time)
        
        # Remove timestamps outside the window
        rate_limit_data[key] = [t for t in rate_limit_data[key] if t > current_time - period]
        
        # Count requests in the current window
        count = len(rate_limit_data[key])
    
    # Check if count exceeds limit
    return count > limit

@socketio.on('connect')
def handle_connect():
    session_id = request.args.get('sessionID')
    token = request.args.get('token')
    origin = request.headers.get('Origin', '')
    
    logging.info(f"Connection attempt with session ID: {session_id} from origin: {origin}")

    # Check for required authentication parameters
    if not session_id:
        logging.warning("Rejecting: Missing session ID")
        return False
        
    # Verify session token if provided
    if token and not ws_manager.verify_token(session_id, token):
        logging.warning(f"Rejecting: Invalid token for session ID: {session_id}")
        return False

    # Rate limit connections per IP to prevent DDoS
    client_ip = request.remote_addr
    if check_rate_limit(f"socket_connect:{client_ip}", 20, 60):
        logging.warning(f"Rejecting: Rate limit exceeded for IP: {client_ip}")
        return False

    # Get and verify user
    user = get_user_from_session(session_id)
    if not user:
        logging.warning(f"Rejecting: No user found for session ID: {session_id}")
        return False

    logging.info(f"Accepting connection for user: {user.username}")
    
    # Store connection info in both old and new systems
    user_sids[user.user_id] = request.sid
    ws_manager.add_client(session_id, request.sid, user.user_id)

    user.is_online = True
    db.session.commit()

    # Join rooms for all contacts and groups
    for contact in user.contacts:
        if contact.status == ContactStatusEnum.FRIEND:
            room_id = f"dm_{min(user.user_id, contact.contact_id)}_{max(user.user_id, contact.contact_id)}"
            join_room(room_id)
            logging.debug(f"User {user.username} joined room: {room_id}")

    for membership in user.group_memberships:
        room_id = f"group_{membership.group_id}"
        join_room(room_id)
        logging.debug(f"User {user.username} joined group room: {room_id}")

    # Notify contacts that user is online
    for contact in user.contacts:
        contact_socket = ws_manager.get_socket_id_for_user(contact.contact_id)
        if contact_socket:
            emit('user_status', {
                'user_id': user.user_id,
                'username': user.username,
                'status': 'online'
            }, room=contact_socket)

    # Send initial data to user
    emit('connection_successful', {
        'user_id': user.user_id,
        'username': user.username,
        'session_expires': time.time() + ws_manager.session_timeout
    }, room=request.sid)
    
    return True

@socketio.on('disconnect')
def handle_disconnect():
    socket_id = request.sid
    
    # Get the user from the old tracking system
    user_id = None
    for uid, sid in user_sids.items():
        if sid == socket_id:
            user_id = uid
            break
    
    # Get the session from the new tracking system
    session_id = ws_manager.socket_sessions.get(socket_id)
    if session_id:
        user_id = ws_manager.get_user_id(session_id) or user_id
    
    # Clean up session info
    ws_manager.remove_client(socket_id)
    
    # If we found a user, update their status
    if user_id:
        # Remove from old tracking system
        user_sids.pop(user_id, None)
        
        # Update user online status
        user = User.query.get(user_id)
        if user:
            user.is_online = False
            user.last_seen = datetime.utcnow()
            db.session.commit()
            
            # Notify contacts that user is offline
            for contact in user.contacts:
                contact_socket = ws_manager.get_socket_id_for_user(contact.contact_id)
                if contact_socket:
                    emit('user_status', {
                        'user_id': user.user_id,
                        'username': user.username,
                        'status': 'offline',
                        'last_seen': user.last_seen.isoformat()
                    }, room=contact_socket)
    else:
        logging.warning(f"Disconnect: Could not find user for socket {socket_id}")

@socketio.on('ping')
def handle_ping(data=None):
    """Handle ping messages to verify connection is alive"""
    session_id = data.get('sessionID') if data else None
    timestamp = data.get('timestamp') if data else None
    
    response = {
        'timestamp': timestamp,
        'server_time': time.time()
    }
    
    if timestamp:
        response['latency'] = int((time.time() * 1000) - timestamp)
    
    # Update session activity if valid session
    if session_id:
        ws_manager.update_session_activity(session_id)
    
    emit('pong', response, room=request.sid)

@socketio.on('verify_session')
def handle_verify_session(data):
    """Verify if the user's session is still valid"""
    session_id = data.get('sessionID')
    token = data.get('token')
    
    # Check if session exists
    is_valid = bool(get_user_from_session(session_id))
    
    # Verify token if provided
    if is_valid and token:
        is_valid = ws_manager.verify_token(session_id, token)
    
    if is_valid:
        # Send success with session expiry info
        expires_at = time.time() + ws_manager.session_timeout
        emit('session_status', {
            'valid': True,
            'expires_at': expires_at
        }, room=request.sid)
    else:
        # Session is invalid
        emit('session_status', {
            'valid': False,
            'message': 'Your session has expired or is invalid'
        }, room=request.sid)

@socketio.on('send_message')
def handle_message(data):
    """Handle sending messages with security checks"""
    session_id = data.get('sessionID')
    recipient_id = data.get('recipient_id')
    content = data.get('content')
    is_group = data.get('is_group', False)
    msg_type = data.get('type', 'text')

    # Authenticate sender
    sender = get_user_from_session(session_id)
    if not sender:
        emit('error', {'message': 'Authentication required'}, room=request.sid)
        return

    # Basic validation
    if not recipient_id or not content:
        emit('error', {'message': 'Missing required fields'}, room=request.sid)
        return
        
    # Rate limit to prevent spam
    if check_rate_limit(f"send_message:{sender.user_id}", 20, 60):
        emit('error', {'message': 'Rate limit exceeded, please wait'}, room=request.sid)
        return

    # Validate recipient exists
    if is_group:
        # Check if group exists and user is a member
        group_membership = next((m for m in sender.group_memberships if str(m.group_id) == str(recipient_id)), None)
        if not group_membership:
            emit('error', {'message': 'You are not a member of this group'}, room=request.sid)
            return
    else:
        # Check if recipient user exists and is a contact
        recipient = User.query.get(recipient_id)
        if not recipient:
            emit('error', {'message': 'Recipient not found'}, room=request.sid)
            return
            
        # Verify they are contacts
        contact = UserContact.query.filter_by(
            user_id=sender.user_id,
            contact_id=recipient.user_id,
            status=ContactStatusEnum.FRIEND
        ).first()
        
        if not contact:
            emit('error', {'message': 'This user is not in your contacts'}, room=request.sid)
            return

    # Create message with unique ID
    message_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    # Create and save message to database
    message = Message(
        message_id=message_id,
        sender_user_id=sender.user_id,
        recipient_user_id=recipient_id,
        encrypted_content=content,  # Note: should be encrypted in production
        type=MessageTypeEnum(msg_type),
        send_at=now,
        is_group=is_group
    )
    db.session.add(message)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error saving message: {e}")
        emit('error', {'message': 'Failed to save message'}, room=request.sid)
        return

    # Determine room ID for the message
    if is_group:
        room_id = f"group_{recipient_id}"
    else:
        room_id = f"dm_{min(sender.user_id, recipient_id)}_{max(sender.user_id, recipient_id)}"

    # Broadcast message to the room
    emit('new_message', {
        'message_id': message_id,
        'sender_id': sender.user_id,
        'sender_username': sender.username,
        'recipient_id': recipient_id,
        'content': content,
        'type': msg_type,
        'timestamp': now.isoformat(),
        'is_group': is_group
    }, room=room_id)
    
    # Clear typing indicator for the sender
    emit('typing_indicator', {
        'user_id': sender.user_id,
        'username': sender.username,
        'is_typing': False,
        'timestamp': now.timestamp()
    }, room=room_id)

@socketio.on('typing')
def handle_typing(data):
    """Handle when a user is typing"""
    session_id = data.get('sessionID')
    recipient_id = data.get('recipient_id')
    is_typing = data.get('is_typing', True)
    is_group = data.get('is_group', False)

    # Get the sender user
    sender = get_user_from_session(session_id)
    if not sender:
        emit('error', {'message': 'Authentication required'}, room=request.sid)
        return

    # Rate limit typing events to prevent spam
    if check_rate_limit(f"typing:{sender.user_id}", 10, 10):
        # Silently fail for typing events
        return

    # Determine room ID for the message
    if is_group:
        room_id = f"group_{recipient_id}"
    else:
        room_id = f"dm_{min(sender.user_id, recipient_id)}_{max(sender.user_id, recipient_id)}"

    # Update typing status
    current_time = datetime.utcnow().timestamp()
    
    if is_typing:
        # Initialize dict for room if it doesn't exist
        if room_id not in typing_users:
            typing_users[room_id] = {}
        
        # Add/update user's typing status
        typing_users[room_id][sender.user_id] = current_time
    else:
        # Remove user from typing status if they stopped typing
        if room_id in typing_users and sender.user_id in typing_users[room_id]:
            typing_users[room_id].pop(sender.user_id, None)
            
            # Remove room if empty
            if not typing_users[room_id]:
                typing_users.pop(room_id, None)

    # Broadcast typing status to room
    emit('typing_indicator', {
        'user_id': sender.user_id,
        'username': sender.username,
        'is_typing': is_typing,
        'timestamp': current_time
    }, room=room_id)

@socketio.on('read_receipt')
def handle_read_receipt(data):
    """Handle read receipts for messages"""
    session_id = data.get('sessionID')
    message_ids = data.get('message_ids', [])
    sender_id = data.get('sender_id')  # ID of the message sender (whose messages were read)
    
    # Validate input
    if not message_ids or not isinstance(message_ids, list):
        emit('error', {'message': 'Invalid message IDs'}, room=request.sid)
        return
        
    if not sender_id:
        emit('error', {'message': 'Sender ID is required'}, room=request.sid)
        return
    
    reader = get_user_from_session(session_id)
    if not reader:
        emit('error', {'message': 'Authentication required'}, room=request.sid)
        return
    
    # Rate limit to prevent abuse
    if check_rate_limit(f"read_receipt:{reader.user_id}", 10, 10):
        # Silent fail for read receipts - not critical
        return
    
    # Mark messages as read in database
    for message_id in message_ids:
        result = message_service.mark_as_read(message_id, reader.user_id)
        if result.get('error'):
            logging.warning(f"Error marking message {message_id} as read: {result['error']}")
            # Continue with other messages even if one fails
    
    # Notify the original sender that their messages were read
    sender_socket = ws_manager.get_socket_id_for_user(sender_id)
    if sender_socket:
        emit('messages_read', {
            'reader_id': reader.user_id,
            'reader_username': reader.username,
            'message_ids': message_ids,
            'timestamp': datetime.utcnow().isoformat()
        }, room=sender_socket)

@socketio.on('get_chat_history')
def handle_get_chat_history(data):
    """Get chat history with pagination"""
    session_id = data.get('sessionID')
    chat_id = data.get('chat_id')
    is_group = data.get('is_group', False)
    page = data.get('page', 1)
    page_size = data.get('page_size', 20)
    
    user = get_user_from_session(session_id)
    if not user:
        emit('error', {'message': 'Authentication required'}, room=request.sid)
        return
    
    # Get messages from database with pagination
    result = message_service.get_chat_messages(
        user.user_id, 
        chat_id, 
        is_group,
        page=page,
        page_size=page_size
    )
    
    if 'error' in result:
        emit('error', {'message': result['error']}, room=request.sid)
        return
    
    # Send message history to client
    emit('chat_history', {
        'chat_id': chat_id,
        'is_group': is_group,
        'messages': result['messages'],
        'page': page,
        'total_pages': result['total_pages'],
        'total_messages': result['total_messages']
    }, room=request.sid)

@socketio.on('add_contact')
def handle_add_contact(data):
    session_id = data.get('sessionID')
    contact_username = data.get('contact_username')

    user = get_user_from_session(session_id)
    if not user:
        emit('error', {'message': 'Invalid session'}, room=request.sid)
        return

    contact = User.query.filter_by(username=contact_username).first()
    if not contact:
        emit('error', {'message': 'User not found'}, room=request.sid)
        return

    # Check if contact already exists
    existing = UserContact.query.filter_by(
        user_id=user.user_id, 
        contact_id=contact.user_id
    ).first()
    
    if existing:
        emit('error', {'message': 'Contact already added'}, room=request.sid)
        return

    # Create contact relationship
    new_contact = UserContact(
        user_id=user.user_id,
        contact_id=contact.user_id,
        status=ContactStatusEnum.NEW,
        streak=0,
        continue_streak=True
    )
    db.session.add(new_contact)
    db.session.commit()

    # Notify the requester
    contact_data = {
        'user_id': contact.user_id,
        'username': contact.username,
        'status': ContactStatusEnum.NEW.value
    }
    emit('contact_added', contact_data, room=request.sid)

    # Notify the contact if they're online
    if contact.user_id in user_sids:
        emit('contact_request', {
            'user_id': user.user_id,
            'username': user.username
        }, room=user_sids[contact.user_id])

@socketio.on('get_chats')
def handle_get_chats(data):
    """Get all chats for the user"""
    session_id = data.get('sessionID')
    
    user = get_user_from_session(session_id)
    if not user:
        emit('error', {'message': 'Authentication required'}, room=request.sid)
        return
    
    # Rate limit to prevent abuse
    if check_rate_limit(f"get_chats:{user.user_id}", 5, 10):
        emit('error', {'message': 'Rate limit exceeded, please wait'}, room=request.sid)
        return
    
    # Get all direct message chats
    dm_chats = []
    for contact in user.contacts:
        # Get the other user's details
        contact_user = User.query.get(contact.contact_id)
        if not contact_user:
            continue
            
        # Get the last message between them if any
        last_message = message_service.get_last_message(user.user_id, contact.contact_id, False)
        
        # Get unread count
        unread_count = message_service.get_unread_count(user.user_id, contact.contact_id, False)
        
        dm_chats.append({
            'id': contact.contact_id,
            'username': contact_user.username,
            'status': 'online' if contact_user.is_online else 'offline',
            'last_seen': contact_user.last_seen.isoformat() if contact_user.last_seen else None,
            'last_message': last_message,
            'unread_count': unread_count,
            'is_group': False
        })
    
    # Get all group chats
    group_chats = []
    for membership in user.group_memberships:
        group = membership.group
        
        # Get the last message in the group if any
        last_message = message_service.get_last_message(user.user_id, group.group_id, True)
        
        # Get unread count
        unread_count = message_service.get_unread_count(user.user_id, group.group_id, True)
        
        group_chats.append({
            'id': group.group_id,
            'name': group.name,
            'description': group.description,
            'member_count': len(group.members),
            'last_message': last_message,
            'unread_count': unread_count,
            'is_group': True
        })
    
    # Combine and send all chats
    combined_chats = dm_chats + group_chats
    combined_chats.sort(key=lambda x: (x.get('last_message', {}).get('timestamp', '0') or '0'), reverse=True)
    
    emit('chats', combined_chats, room=request.sid)

@socketio.on('accept_contact')
def handle_accept_contact(data):
    """Accept a contact request"""
    session_id = data.get('sessionID')
    contact_id = data.get('contact_id')
    
    user = get_user_from_session(session_id)
    if not user:
        emit('error', {'message': 'Authentication required'}, room=request.sid)
        return
    
    # Find the contact relationship
    contact_rel = UserContact.query.filter_by(
        user_id=user.user_id,
        contact_id=contact_id
    ).first()
    
    if not contact_rel:
        emit('error', {'message': 'Contact request not found'}, room=request.sid)
        return
    
    # Update status to FRIEND
    contact_rel.status = ContactStatusEnum.FRIEND
    
    # Check if reverse relationship exists, create if not
    reverse_rel = UserContact.query.filter_by(
        user_id=contact_id,
        contact_id=user.user_id
    ).first()
    
    if not reverse_rel:
        reverse_rel = UserContact(
            user_id=contact_id,
            contact_id=user.user_id,
            status=ContactStatusEnum.FRIEND,
            streak=0,
            continue_streak=True
        )
        db.session.add(reverse_rel)
    else:
        reverse_rel.status = ContactStatusEnum.FRIEND
    
    db.session.commit()
    
    # Get the contact user
    contact_user = User.query.get(contact_id)
    
    # Notify the user who accepted
    emit('contact_accepted', {
        'user_id': contact_id,
        'username': contact_user.username,
        'status': ContactStatusEnum.FRIEND.value
    }, room=request.sid)
    
    # Notify the other user if they're online
    contact_socket = ws_manager.get_socket_id_for_user(contact_id)
    if contact_socket:
        emit('contact_accepted', {
            'user_id': user.user_id,
            'username': user.username,
            'status': ContactStatusEnum.FRIEND.value
        }, room=contact_socket)
        
    # Make them join each other's chat rooms
    user_socket = request.sid
    room_id = f"dm_{min(user.user_id, contact_id)}_{max(user.user_id, contact_id)}"
    join_room(room_id, sid=user_socket)
    
    if contact_socket:
        join_room(room_id, sid=contact_socket)

@socketio.on('reject_contact')
def handle_reject_contact(data):
    """Reject a contact request"""
    session_id = data.get('sessionID')
    contact_id = data.get('contact_id')
    
    user = get_user_from_session(session_id)
    if not user:
        emit('error', {'message': 'Authentication required'}, room=request.sid)
        return
    
    # Find the contact relationship
    contact_rel = UserContact.query.filter_by(
        user_id=user.user_id,
        contact_id=contact_id
    ).first()
    
    if not contact_rel:
        emit('error', {'message': 'Contact request not found'}, room=request.sid)
        return
    
    # Delete the contact relationship
    db.session.delete(contact_rel)
    db.session.commit()
    
    # Notify the user who rejected
    emit('contact_rejected', {
        'user_id': contact_id
    }, room=request.sid)
    
    # Optionally notify the other user if they're online
    contact_socket = ws_manager.get_socket_id_for_user(contact_id)
    if contact_socket:
        emit('contact_rejected', {
            'user_id': user.user_id
        }, room=contact_socket)

@socketio.on('get_contacts')
def handle_get_contacts(data):
    """Get all contacts for the user with their status"""
    session_id = data.get('sessionID')
    
    user = get_user_from_session(session_id)
    if not user:
        emit('error', {'message': 'Authentication required'}, room=request.sid)
        return
    
    contacts = []
    for contact_rel in user.contacts:
        contact_user = User.query.get(contact_rel.contact_id)
        if not contact_user:
            continue
            
        contacts.append({
            'user_id': contact_user.user_id,
            'username': contact_user.username,
            'status': contact_rel.status.value,
            'is_online': contact_user.is_online,
            'last_seen': contact_user.last_seen.isoformat() if contact_user.last_seen else None,
            'streak': contact_rel.streak,
            'continue_streak': contact_rel.continue_streak
        })
    
    emit('contacts', {'contacts': contacts}, room=request.sid)

@socketio.on('block_contact')
def handle_block_contact(data):
    """Block a contact"""
    session_id = data.get('sessionID')
    contact_id = data.get('contact_id')
    
    user = get_user_from_session(session_id)
    if not user:
        emit('error', {'message': 'Authentication required'}, room=request.sid)
        return
    
    # Find the contact relationship
    contact_rel = UserContact.query.filter_by(
        user_id=user.user_id,
        contact_id=contact_id
    ).first()
    
    if not contact_rel:
        emit('error', {'message': 'Contact not found'}, room=request.sid)
        return
    
    # Update status to BLOCKED
    contact_rel.status = ContactStatusEnum.BLOCKED
    db.session.commit()
    
    # Notify the user who blocked
    emit('contact_blocked', {
        'user_id': contact_id
    }, room=request.sid)
    
    # Leave the shared chat room
    room_id = f"dm_{min(user.user_id, contact_id)}_{max(user.user_id, contact_id)}"
    leave_room(room_id)

@socketio.on('delete_message')
def handle_delete_message(data):
    """Delete a message (mark as deleted, don't actually remove from DB)"""
    session_id = data.get('sessionID')
    message_id = data.get('message_id')
    
    user = get_user_from_session(session_id)
    if not user:
        emit('error', {'message': 'Authentication required'}, room=request.sid)
        return
    
    # Get the message
    message = Message.query.filter_by(message_id=message_id).first()
    if not message:
        emit('error', {'message': 'Message not found'}, room=request.sid)
        return
    
    # Check if user is the sender
    if message.sender_user_id != user.user_id:
        emit('error', {'message': 'You can only delete your own messages'}, room=request.sid)
        return
    
    # Mark as deleted but keep in database
    message.is_deleted = True
    db.session.commit()
    
    # Determine room ID for notification
    if message.is_group:
        room_id = f"group_{message.recipient_user_id}"
    else:
        room_id = f"dm_{min(message.sender_user_id, message.recipient_user_id)}_{max(message.sender_user_id, message.recipient_user_id)}"
    
    # Notify the room that message was deleted
    emit('message_deleted', {
        'message_id': message_id,
        'sender_id': user.user_id,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room_id)

@socketio.on('get_chat_info')
def handle_get_chat_info(data):
    """Get information about a specific chat"""
    session_id = data.get('sessionID')
    chat_id = data.get('chat_id')
    is_group = data.get('is_group', False)
    
    user = get_user_from_session(session_id)
    if not user:
        emit('error', {'message': 'Authentication required'}, room=request.sid)
        return
    
    # Group chat
    if is_group:
        # Check if user is a member of this group
        membership = next((m for m in user.group_memberships if str(m.group_id) == str(chat_id)), None)
        if not membership:
            emit('error', {'message': 'You are not a member of this group'}, room=request.sid)
            return
            
        group = membership.group
        members = []
        
        for member in group.members:
            members.append({
                'user_id': member.user_id,
                'username': member.user.username,
                'is_online': member.user.is_online,
                'last_seen': member.user.last_seen.isoformat() if member.user.last_seen else None,
                'is_admin': member.is_admin
            })
            
        emit('chat_info', {
            'id': group.group_id,
            'name': group.name,
            'description': group.description,
            'created_at': group.created_at.isoformat(),
            'is_group': True,
            'members': members,
            'member_count': len(members),
            'is_admin': membership.is_admin
        }, room=request.sid)
    
    # Direct message chat
    else:
        # Check if the user has this contact
        contact = next((c for c in user.contacts if str(c.contact_id) == str(chat_id)), None)
        if not contact:
            emit('error', {'message': 'This user is not in your contacts'}, room=request.sid)
            return
            
        contact_user = User.query.get(chat_id)
        if not contact_user:
            emit('error', {'message': 'User not found'}, room=request.sid)
            return
            
        emit('chat_info', {
            'id': contact_user.user_id,
            'username': contact_user.username,
            'is_online': contact_user.is_online,
            'last_seen': contact_user.last_seen.isoformat() if contact_user.last_seen else None,
            'status': contact.status.value,
            'is_group': False,
            'streak': contact.streak,
            'continue_streak': contact.continue_streak
        }, room=request.sid)

@socketio.on('upload_file_prepare')
def handle_upload_file_prepare(data):
    """Prepare for file upload by validating and getting a secure upload URL"""
    session_id = data.get('sessionID')
    recipient_id = data.get('recipient_id')
    is_group = data.get('is_group', False)
    file_name = data.get('file_name')
    file_size = data.get('file_size')
    file_type = data.get('file_type')
    
    user = get_user_from_session(session_id)
    if not user:
        emit('error', {'message': 'Authentication required'}, room=request.sid)
        return
    
    # Validate inputs
    if not recipient_id or not file_name or not file_type:
        emit('error', {'message': 'Missing required fields'}, room=request.sid)
        return
    
    # File size limits
    max_size = 10 * 1024 * 1024  # 10MB limit
    if file_size > max_size:
        emit('error', {'message': 'File exceeds maximum size of 10MB'}, room=request.sid)
        return
    
    # Validate file type (basic security check)
    allowed_types = [
        'image/jpeg', 'image/png', 'image/gif', 'image/webp',
        'application/pdf', 'text/plain',
        'audio/mpeg', 'audio/wav', 'audio/ogg',
        'video/mp4', 'video/webm'
    ]
    
    if file_type not in allowed_types:
        emit('error', {'message': 'File type not allowed'}, room=request.sid)
        return
    
    # Generate a unique file ID
    file_id = str(uuid.uuid4())
    
    # In a real implementation, you would:
    # 1. Generate a secure, signed upload URL (e.g., S3 presigned URL)
    # 2. Store pending upload information in database
    
    # For this example, we'll simulate this with a token
    upload_token = hmac.new(
        ws_manager.token_secret.encode(),
        f"{file_id}:{user.user_id}:{recipient_id}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Return upload information to client
    emit('file_upload_ready', {
        'file_id': file_id,
        'upload_url': f"/api/upload/{file_id}",  # This would be a real upload URL in production
        'upload_token': upload_token,
        'expires_in': 3600  # URL valid for 1 hour
    }, room=request.sid)

@socketio.on('upload_file_complete')
def handle_upload_file_complete(data):
    """Handle completed file upload by sending a file message"""
    session_id = data.get('sessionID')
    file_id = data.get('file_id')
    recipient_id = data.get('recipient_id')
    is_group = data.get('is_group', False)
    file_name = data.get('file_name')
    file_type = data.get('file_type')
    
    user = get_user_from_session(session_id)
    if not user:
        emit('error', {'message': 'Authentication required'}, room=request.sid)
        return
    
    # Validate required fields
    if not file_id or not recipient_id:
        emit('error', {'message': 'Missing required fields'}, room=request.sid)
        return
    
    # Determine message type based on file type
    if file_type.startswith('image/'):
        msg_type = 'image'
    elif file_type.startswith('video/'):
        msg_type = 'video'
    elif file_type.startswith('audio/'):
        msg_type = 'audio'
    else:
        msg_type = 'file'
    
    # Create file URL (in real implementation, this would be your CDN or file server URL)
    file_url = f"/api/files/{file_id}/{file_name}"
    
    # Create message content with file metadata
    content = json.dumps({
        'file_id': file_id,
        'file_name': file_name,
        'file_type': file_type,
        'file_url': file_url
    })
    
    # Create and save message to database
    message_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    message = Message(
        message_id=message_id,
        sender_user_id=user.user_id,
        recipient_user_id=recipient_id,
        encrypted_content=content,
        type=MessageTypeEnum(msg_type),
        send_at=now,
        is_group=is_group
    )
    db.session.add(message)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error saving file message: {e}")
        emit('error', {'message': 'Failed to save message'}, room=request.sid)
        return
    
    # Determine room ID for the message
    if is_group:
        room_id = f"group_{recipient_id}"
    else:
        room_id = f"dm_{min(user.user_id, recipient_id)}_{max(user.user_id, recipient_id)}"
    
    # Broadcast message to the room
    emit('new_message', {
        'message_id': message_id,
        'sender_id': user.user_id,
        'sender_username': user.username,
        'recipient_id': recipient_id,
        'content': content,
        'type': msg_type,
        'timestamp': now.isoformat(),
        'is_group': is_group
    }, room=room_id)
