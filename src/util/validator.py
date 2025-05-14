import re
from datetime import datetime


def is_valid_phone(phone: str) -> bool:
    """Validate South Korean mobile number format: 010xxxxxxxx"""
    return bool(re.fullmatch(r"^010\d{8}$", phone))


_current_year = datetime.now().year


def is_valid_student_id(student_id: str) -> bool:
    """Validate student ID format: 9 digits, first 4 should be a plausible year."""
    match = re.fullmatch(r"^(\d{4})(\d{5})$", student_id)
    if not match:
        return False

    year = int(match.group(1))
    # You can adjust this range as needed
    return 1946 <= year <= _current_year
