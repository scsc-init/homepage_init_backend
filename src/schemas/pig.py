from datetime import datetime
from typing import Optional

from src.model import SCSCStatus

from .base import BaseResponse
from .user import UserResponse


class PigMemberResponse(BaseResponse):
    id: int
    ig_id: int
    user_id: str
    created_at: datetime
    user: Optional[UserResponse] = None


class PigResponse(BaseResponse):
    id: int
    title: str
    description: str
    content_id: int
    status: SCSCStatus
    year: int
    semester: int
    owner: str
    should_extend: bool
    is_rolling_admission: bool
    created_at: datetime
    updated_at: datetime
