from datetime import datetime

from pydantic import Field

from src.model import SCSCStatus

from .base import BaseResponse
from .user import UserResponse


class TagResponse(BaseResponse):
    id: int
    text: str
    is_major: bool


class SigMemberResponse(BaseResponse):
    id: int
    ig_id: int
    user_id: str
    created_at: datetime
    user: UserResponse | None = None


class SigResponse(BaseResponse):
    id: int
    title: str
    description: str
    content_id: int
    status: SCSCStatus
    created_year: int
    created_semester: int
    year: int
    semester: int
    owner: str
    should_extend: bool
    is_rolling_admission: bool
    created_at: datetime
    updated_at: datetime
    tags: list[TagResponse] = Field(default_factory=list)


class SigTagResponse(BaseResponse):
    id: int
    sig_id: int
    tag_id: int
