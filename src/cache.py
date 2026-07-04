import hashlib
from src.store import get_cached_verdict, store_verdict


def fingerprint(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_cache(media_bytes: bytes) -> dict | None:
    return get_cached_verdict(fingerprint(media_bytes))


def save_to_cache(media_bytes: bytes, verdict: dict):
    store_verdict(fingerprint(media_bytes), verdict)
