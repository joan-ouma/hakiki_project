import re
import hashlib
import os

SALT = os.getenv("PRIVACY_SALT", "default-hakiki-salt")

def hash_phone_number(phone_number: str) -> str:
    """
    Hashes a phone number with a salt so it can be uniquely identified
    in memory/session without being stored in plaintext.
    """
    if not phone_number:
        return ""
    return hashlib.sha256((phone_number + SALT).encode('utf-8')).hexdigest()

def strip_pii(text: str) -> str:
    """
    Strips phone numbers and obvious PII from raw text strings.
    This ensures logging by construction redacts phone numbers.
    """
    if not text:
        return text
        
    # Simple regex to redact phone numbers (Kenyan format and general international)
    # Matches +254... or 07... or 01... with optional spaces
    phone_pattern = r'(?:\+?254|0)[17]\d{1,2}[\s\-]?\d{3}[\s\-]?\d{3}'
    redacted_text = re.sub(phone_pattern, '[REDACTED_PHONE]', text)
    
    return redacted_text
