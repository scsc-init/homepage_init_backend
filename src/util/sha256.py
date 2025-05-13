import hashlib


def sha256_hash(text: str) -> str:
    """Generate a SHA-256 hash from the input text (e.g. email). Make email lowercase."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
