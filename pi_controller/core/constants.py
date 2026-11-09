CREATE_MESSAGES_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TEXT NOT NULL
    );
"""

CREATE_INDICES_QUERY = """
    CREATE INDEX IF NOT EXISTS idx_messages_session_id
    ON messages(session_id, id);
"""