import hashlib
import os

_SALT = os.environ.get("PRIVACY_SALT", "hakiki-default-salt")


def hash_phone(phone: str) -> str:
    return hashlib.sha256(f"{_SALT}{phone}".encode()).hexdigest()[:16]


def strip_pii(payload: dict) -> dict:
    out = dict(payload)
    if "From" in out:
        out["From"] = hash_phone(out["From"])
    return out
