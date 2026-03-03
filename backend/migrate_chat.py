import sqlite3
conn = sqlite3.connect("law.db")
migrations = [
    "ALTER TABLE chat_sessions ADD COLUMN username TEXT DEFAULT 'anonymous'",
    "ALTER TABLE chat_sessions ADD COLUMN title TEXT DEFAULT 'New Chat'",
    "ALTER TABLE chat_sessions ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP",
    "ALTER TABLE chat_messages ADD COLUMN law_updates TEXT DEFAULT '[]'",
]
for sql in migrations:
    try:
        conn.execute(sql)
        print(f"OK: {sql[:50]}")
    except Exception as e:
        print(f"SKIP: {e}")
conn.commit()
conn.close()
print("Migration done")
