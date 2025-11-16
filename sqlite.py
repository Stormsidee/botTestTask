import sqlite3
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SQLiteChatHistory:
    def __init__(self, db_path="chat_history.db"):
        self.db_path = db_path
        self.max_history_length = 10 
        self._init_db()
    
    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS chat_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_user_id_timestamp 
                    ON chat_history (user_id, timestamp)
                ''')
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def add_message(self, user_id, role, content):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)",
                    (user_id, role, content)
                )
                logger.debug(f"Message added for user {user_id}")
        except Exception as e:
            logger.error(f"Error adding message: {e}")
    
    def get_history(self, user_id, limit=None):
        if limit is None:
            limit = self.max_history_length
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    '''SELECT role, content FROM chat_history 
                       WHERE user_id = ? 
                       ORDER BY timestamp ASC 
                       LIMIT ?''',
                    (user_id, limit)
                )
                messages = cursor.fetchall()
                return [{"role": role, "content": content} for role, content in messages]
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return []
    
    def clear_history(self, user_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "DELETE FROM chat_history WHERE user_id = ?",
                    (user_id,)
                )
                logger.debug(f"History cleared for user {user_id}")
        except Exception as e:
            logger.error(f"Error clearing history: {e}")