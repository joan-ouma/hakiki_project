import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'hakiki.db')

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table for pre-scraped NG-CDF/Audit claims
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS seed_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_type TEXT NOT NULL, -- e.g., 'ng-cdf', 'auditor-general', 'news'
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        url TEXT,
        date_published TEXT
    )
    ''')
    
    # Table for caching media hashes to avoid re-running HF models
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS media_cache (
        hash TEXT PRIMARY KEY,
        media_type TEXT NOT NULL, -- 'audio' or 'image'
        transcription TEXT,       -- only if audio
        verdict_score REAL,       -- deepfake probability or similar
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def insert_seed_record(source_type: str, title: str, content: str, url: str, date_published: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO seed_records (source_type, title, content, url, date_published)
    VALUES (?, ?, ?, ?, ?)
    ''', (source_type, title, content, url, date_published))
    conn.commit()
    conn.close()

def search_seed_records(query: str):
    conn = get_connection()
    cursor = conn.cursor()
    # Simple FTS or LIKE query (For V1 we use LIKE)
    cursor.execute('''
    SELECT * FROM seed_records 
    WHERE content LIKE ? OR title LIKE ?
    LIMIT 5
    ''', (f'%{query}%', f'%{query}%'))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
