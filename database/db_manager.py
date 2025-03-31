import sqlite3
import json
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    """Manages SQLite database operations for the application"""
    
    def __init__(self, db_path=None):
        """Initialize the database manager with a database file path"""
        if db_path is None:
            # Default to a 'data' directory in the application folder
            db_dir = Path.cwd() / 'data'
            db_dir.mkdir(exist_ok=True)
            self.db_path = db_dir / 'ollama_chat.db'
        else:
            self.db_path = Path(db_path)
            
        self.init_db()
    
    def init_db(self):
        """Initialize the database with necessary tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                model TEXT NOT NULL,
                system_prompt TEXT,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
            ''')
            
            # Create messages table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                has_image BOOLEAN DEFAULT 0,
                image_path TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
            )
            ''')
            
            # Create tags table for categorizing conversations
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            )
            ''')
            
            # Create conversation_tags junction table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_tags (
                conversation_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (conversation_id, tag_id),
                FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
            )
            ''')
            
            # Create settings table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            ''')
            
            conn.commit()
    
    def save_conversation(self, title, model, messages, system_prompt=None):
        """
        Save a conversation and its messages to the database
        
        Args:
            title: Title of the conversation
            model: AI model used in the conversation
            messages: List of message dictionaries with role and content
            system_prompt: Optional system prompt used for this conversation
            
        Returns:
            conversation_id: ID of the saved conversation
        """
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert conversation
            cursor.execute('''
            INSERT INTO conversations (title, model, system_prompt, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (title, model, system_prompt, now, now))
            
            conversation_id = cursor.lastrowid
            
            # Insert messages
            for msg in messages:
                has_image = 0
                image_path = None
                
                # Check if message has an image
                if isinstance(msg.get('content'), dict) and 'image_path' in msg['content']:
                    has_image = 1
                    image_path = msg['content']['image_path']
                    content = msg['content'].get('text', '')
                else:
                    content = msg.get('content', '')
                
                cursor.execute('''
                INSERT INTO messages (conversation_id, role, content, timestamp, has_image, image_path)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (conversation_id, msg['role'], content, now, has_image, image_path))
            
            conn.commit()
            
            return conversation_id
    
    def get_conversation(self, conversation_id):
        """
        Retrieve a conversation and its messages by ID
        
        Args:
            conversation_id: ID of the conversation to retrieve
            
        Returns:
            conversation: Dictionary with conversation details and messages
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get conversation
            cursor.execute('''
            SELECT * FROM conversations WHERE id = ?
            ''', (conversation_id,))
            
            conversation_row = cursor.fetchone()
            if not conversation_row:
                return None
            
            conversation = dict(conversation_row)
            
            # Get messages
            cursor.execute('''
            SELECT * FROM messages 
            WHERE conversation_id = ? 
            ORDER BY timestamp, id
            ''', (conversation_id,))
            
            messages = []
            for msg_row in cursor.fetchall():
                msg = dict(msg_row)
                
                # Handle messages with images
                if msg['has_image'] and msg['image_path']:
                    message_content = {
                        'text': msg['content'],
                        'image_path': msg['image_path']
                    }
                    messages.append({
                        'role': msg['role'],
                        'content': message_content
                    })
                else:
                    messages.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
            
            conversation['messages'] = messages
            return conversation
    
    def list_conversations(self, limit=20, offset=0, search=None):
        """
        List conversations, optionally filtered by search term
        
        Args:
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip (for pagination)
            search: Optional search term to filter conversations
            
        Returns:
            conversations: List of conversation dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
            SELECT c.id, c.title, c.model, c.created_at, c.updated_at,
                   COUNT(m.id) as message_count,
                   GROUP_CONCAT(t.name, ', ') as tags
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
            LEFT JOIN conversation_tags ct ON c.id = ct.conversation_id
            LEFT JOIN tags t ON ct.tag_id = t.id
            '''
            
            params = []
            if search:
                query += '''
                WHERE c.title LIKE ? OR m.content LIKE ?
                '''
                search_term = f'%{search}%'
                params.extend([search_term, search_term])
            
            query += '''
            GROUP BY c.id
            ORDER BY c.updated_at DESC
            LIMIT ? OFFSET ?
            '''
            
            params.extend([limit, offset])
            cursor.execute(query, params)
            
            conversations = [dict(row) for row in cursor.fetchall()]
            return conversations
    
    def update_conversation(self, conversation_id, title=None, messages=None):
        """
        Update an existing conversation
        
        Args:
            conversation_id: ID of the conversation to update
            title: New title (if provided)
            messages: New messages list (if provided)
            
        Returns:
            success: Boolean indicating success
        """
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if title:
                cursor.execute('''
                UPDATE conversations
                SET title = ?, updated_at = ?
                WHERE id = ?
                ''', (title, now, conversation_id))
            
            if messages:
                # Delete existing messages
                cursor.execute('''
                DELETE FROM messages
                WHERE conversation_id = ?
                ''', (conversation_id,))
                
                # Insert new messages
                for msg in messages:
                    has_image = 0
                    image_path = None
                    
                    # Check if message has an image
                    if isinstance(msg.get('content'), dict) and 'image_path' in msg['content']:
                        has_image = 1
                        image_path = msg['content']['image_path']
                        content = msg['content'].get('text', '')
                    else:
                        content = msg.get('content', '')
                    
                    cursor.execute('''
                    INSERT INTO messages (conversation_id, role, content, timestamp, has_image, image_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (conversation_id, msg['role'], content, now, has_image, image_path))
                
                # Update conversation last modified time
                cursor.execute('''
                UPDATE conversations
                SET updated_at = ?
                WHERE id = ?
                ''', (now, conversation_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_conversation(self, conversation_id):
        """
        Delete a conversation and its messages
        
        Args:
            conversation_id: ID of the conversation to delete
            
        Returns:
            success: Boolean indicating success
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
            DELETE FROM conversations
            WHERE id = ?
            ''', (conversation_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def add_tag_to_conversation(self, conversation_id, tag_name):
        """
        Add a tag to a conversation
        
        Args:
            conversation_id: ID of the conversation
            tag_name: Name of the tag to add
            
        Returns:
            success: Boolean indicating success
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get or create tag
            cursor.execute('''
            INSERT OR IGNORE INTO tags (name)
            VALUES (?)
            ''', (tag_name,))
            
            cursor.execute('''
            SELECT id FROM tags WHERE name = ?
            ''', (tag_name,))
            
            tag_id = cursor.fetchone()[0]
            
            # Add tag to conversation
            cursor.execute('''
            INSERT OR IGNORE INTO conversation_tags (conversation_id, tag_id)
            VALUES (?, ?)
            ''', (conversation_id, tag_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def search_by_content(self, search_term, limit=20, offset=0):
        """
        Search for conversations containing specific content
        
        Args:
            search_term: Term to search for in messages
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            results: List of matching conversations with message snippets
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
            SELECT c.id, c.title, c.model, m.content AS snippet, 
                   c.created_at, c.updated_at
            FROM conversations c
            JOIN messages m ON c.id = m.conversation_id
            WHERE m.content LIKE ?
            ORDER BY c.updated_at DESC
            LIMIT ? OFFSET ?
            '''
            
            search_term = f'%{search_term}%'
            cursor.execute(query, (search_term, limit, offset))
            
            results = [dict(row) for row in cursor.fetchall()]
            return results
    
    def get_stats(self):
        """
        Get database statistics
        
        Returns:
            stats: Dictionary with database statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get conversation count
            cursor.execute('SELECT COUNT(*) FROM conversations')
            conversation_count = cursor.fetchone()[0]
            
            # Get message count
            cursor.execute('SELECT COUNT(*) FROM messages')
            message_count = cursor.fetchone()[0]
            
            # Get model usage
            cursor.execute('''
            SELECT model, COUNT(*) as count
            FROM conversations
            GROUP BY model
            ORDER BY count DESC
            ''')
            model_usage = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Get tag counts
            cursor.execute('''
            SELECT t.name, COUNT(ct.conversation_id) as count
            FROM tags t
            JOIN conversation_tags ct ON t.id = ct.tag_id
            GROUP BY t.name
            ORDER BY count DESC
            ''')
            tag_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                'conversation_count': conversation_count,
                'message_count': message_count,
                'model_usage': model_usage,
                'tag_counts': tag_counts
            }
    
    # Settings management
    def set_setting(self, key, value):
        """Save a setting to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Convert value to JSON string if it's not a string
            if not isinstance(value, str):
                value = json.dumps(value)
            
            cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value)
            VALUES (?, ?)
            ''', (key, value))
            
            conn.commit()
    
    def get_setting(self, key, default=None):
        """Retrieve a setting from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT value FROM settings
            WHERE key = ?
            ''', (key,))
            
            result = cursor.fetchone()
            if result:
                # Try to parse as JSON, return as string if it fails
                try:
                    return json.loads(result[0])
                except json.JSONDecodeError:
                    return result[0]
            return default