
"""
Initialise a SQLite database
Create a messages table
save user and assistant messages
retrieve messages for a givn session_id, in chronological order
"""
import sqlite3
from typing import List, Tuple
import logging
from pi_controller.core.constants import CREATE_INDICES_QUERY, CREATE_MESSAGES_TABLE_QUERY
from datetime import datetime, timezone

from shared.contracts import ChatMessageRole, ChatMessageSchema
logger = logging.getLogger(__name__)
class ConversationStore:
    
    def __init__(self, db_path: str = "conversation_store.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        self._initialize_tables()
        self._initialize_indices()

    def _initialize_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor() # to execute SQL commands
            create_table_query = CREATE_MESSAGES_TABLE_QUERY
            cursor.execute(create_table_query)
            conn.commit()
            logger.info("Database and messages table initialized.")

    def _initialize_indices(self):
        create_index_query = CREATE_INDICES_QUERY
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(create_index_query)
            conn.commit()
            logger.info("Indices initialized.")


    def add_message(self, session_id: str, role: ChatMessageRole, content: str, timestamp: str | None = None):
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            insert_query = """
                INSERT INTO messages (session_id, role, content, timestamp)
                VALUES (?, ?, ?, ?);
            """
            cursor.execute(insert_query, (session_id, role.value, content, timestamp))
            conn.commit()
        logger.info(f"Message added to session_id: {session_id}")

    def get_messages(self, session_id: str, limit: int = 20) -> List[ChatMessageSchema]:
        if limit < 1:
            raise ValueError("Limit must be a positive integer")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            select_query = """
                SELECT role, content, timestamp
                FROM (
                    SELECT id, role, content, timestamp
                    FROM messages
                    WHERE session_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                )
                ORDER BY id ASC;
            """
            cursor.execute(select_query, (session_id, limit))
            messages = cursor.fetchall()
            logger.info(f"Retrieved {len(messages)} messages for session_id: {session_id}")
            return [
                ChatMessageSchema(session_id=session_id, role=ChatMessageRole(message[0]), content=message[1], timestamp=message[2])
                for message in messages
            ]