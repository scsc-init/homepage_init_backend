import hashlib
import re
import uuid
from datetime import datetime

import requests
from fastapi import HTTPException, UploadFile

from src.core import get_settings

from .helper import split_filename


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


async def validate_and_read_file(file: UploadFile, *, valid_mime_type: str = '', valid_ext: frozenset[str] = frozenset()) -> tuple[bytes, str, str, str]:
    """
    Validates an uploaded file against specified MIME type, extension, and size 
    limits, then asynchronously reads its content.

    This function performs the following checks:
    1. Ensures the file's MIME type is provided and starts with `valid_mime_type`.
    2. Ensures the file has a filename.
    3. Ensures the file's extension is one of the extensions in `valid_ext`.
    4. Ensures the file size does not exceed the limit set by `get_settings().file_max_size`.

    Args:
        file: The uploaded file object (e.g., from FastAPI's `File` dependency).
        valid_mime_type: The required starting string for the file's MIME type 
                         (e.g., 'image/' for any image). Defaults to an empty string, 
                         which effectively allows any MIME type if it's not None.
        valid_ext: A frozenset of valid file extensions (e.g., {'jpg', 'png'}). 
                   Defaults to an empty set, which means no extension is allowed 
                   unless an empty string is passed as the extension.

    Raises:
        HTTPException: 
            - 400 (Bad Request): If the MIME type is missing/invalid, 
              filename is missing, or extension is invalid.
            - 413 (Payload Too Large): If the file size exceeds the configured maximum.

    Returns:
        A tuple containing:
        - content (bytes): The binary content of the file.
        - basename (str): The base name of the file (without the extension).
        - ext (str): The file extension (without the leading dot).
        - file.content_type (str): The MIME type of the file.
    """
    if file.content_type is None or not file.content_type.startswith(valid_mime_type): raise HTTPException(400, detail=f"cannot upload file without MIME type {valid_mime_type}")
    if not file.filename: raise HTTPException(400, detail="cannot upload file without filename")
    basename, ext = split_filename(file.filename)
    if ext not in valid_ext: raise HTTPException(400, detail=f"cannot upload if the extension is not {valid_ext}")
    content = await file.read()
    if len(content) > get_settings().file_max_size: raise HTTPException(413, detail=f"cannot upload file larger than {get_settings().file_max_size} bytes")
    return content, basename, ext, file.content_type
    