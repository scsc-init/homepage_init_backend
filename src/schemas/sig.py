from datetime import datetime

from src.model import SCSCStatus

from .base import BaseResponse
from .user import UserSummaryResponse


class TagResponse(BaseResponse):
    id: int
    text: str
    is_major: bool
    created_at: datetime


class SigMemberResponse(BaseResponse):
    id: int
    ig_id: int
    user_id: str
    created_at: datetime
    user: UserSummaryResponse


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
    owner_user: UserSummaryResponse
    members: list[SigMemberResponse]
    tags: list[TagResponse]


class SigTagResponse(BaseResponse):
    id: int
    sig_id: int
    tag_id: int
    created_at: datetime
