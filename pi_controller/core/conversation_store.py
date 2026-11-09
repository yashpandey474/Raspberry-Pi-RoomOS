
"""
Initialise a SQLite database
Create a messages table
save user and assistant messages
retrieve messages for a givn session_id, in chronological order
"""
import sqlite3
from typing import List, Tuple
import logging
from pi_controller.core.constants import CREATE_MESSAGES_TABLE_QUERY
from pi_controller.core.models import LLMMessageRole

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

class ConversationStore:
    def __init__(self, db_path: str = "conversation_store.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor() # to execute SQL commands

            create_table_query = CREATE_MESSAGES_TABLE_QUERY
            cursor.execute(create_table_query)
            conn.commit()
            logger.info("Database and messages table initialized.")

    def add_message(self, session_id: str, role: LLMMessageRole, content: str, timestamp: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            insert_query = """
                INSERT INTO messages (session_id, role, content, timestamp)
                VALUES (?, ?, ?, ?);
            """
            cursor.execute(insert_query, (session_id, role.value, content, timestamp))
            conn.commit()
            logger.info(f"Message saved: {role} - {content}")

    def get_messages(self, session_id: str, limit: int = 20) -> List[Tuple[str, str, str]]:
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
            return messages