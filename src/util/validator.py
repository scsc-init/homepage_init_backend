import hashlib
import re
import uuid
from datetime import datetime

import requests


def sha256_hash(text: str) -> str:
    """Generate a SHA-256 hash from the input text (e.g. email). Make email lowercase."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def create_uuid() -> str:
    return str(uuid.uuid4())


def is_valid_phone(phone: str) -> bool:
    """Validate South Korean mobile number format: 010xxxxxxxx"""
    return bool(re.fullmatch(r"^010\d{8}$", phone))


_current_year = datetime.now().year


def is_valid_student_id(student_id: str) -> bool:
    """Validate student ID format: 9 digits, first 4 should be a plausible year."""
    match = re.fullmatch(r"^(\d{4})(\d{5})$", student_id)
    if not match: return False
    year = int(match.group(1))
    # You can adjust this range as needed
    return 1946 <= year <= _current_year


def is_valid_year(year: int):
    return year >= 2025


def is_valid_semester(semester: int):
    return semester in (1, 2)


def is_valid_img_url(url: str, timeout: int = 5) -> bool:
    """
    Checks if the given URL string is likely an image URL by:
    1. Performing basic string and scheme validation.
    2. Making a synchronous HTTP GET request to the URL.
    3. Inspecting the 'Content-Type' header of the response to ensure it's an image.

    This provides a more robust validation than just checking file extensions.

    Args:
        url (str): The URL string to validate.
        timeout (int): The maximum time (in seconds) to wait for the HTTP request to complete.

    Returns:
        bool: True if the URL appears to be a valid image URL (based on content type), False otherwise.
    """
    if not isinstance(url, str): return False
    if not (url.startswith('http://') or url.startswith('https://')): return False

    try:
        response = requests.get(url, allow_redirects=True, timeout=timeout)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '').lower()
        return content_type.startswith('image/')
    except requests.exceptions.RequestException: return False
    except Exception: return False
