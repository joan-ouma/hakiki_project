import hashlib
from src.store import get_connection

def generate_media_hash(media_bytes: bytes) -> str:
    """Generates a SHA-256 hash of the media content."""
    return hashlib.sha256(media_bytes).hexdigest()

def check_media_cache(media_hash: str):
    """
    Checks if we have processed this exact media before.
    Returns a dict with previous results or None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT media_type, transcription, verdict_score 
    FROM media_cache 
    WHERE hash = ?
    ''', (media_hash,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def save_media_cache(media_hash: str, media_type: str, transcription: str = None, verdict_score: float = None):
    """Saves the processed media results to cache."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR IGNORE INTO media_cache (hash, media_type, transcription, verdict_score)
    VALUES (?, ?, ?, ?)
    ''', (media_hash, media_type, transcription, verdict_score))
    conn.commit()
    conn.close()
