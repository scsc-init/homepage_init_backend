from datetime import datetime

from src.model import SCSCStatus
from src.model.pig import RollingAdmission

from .base import BaseResponse
from .user import UserSummaryResponse


class PigMemberResponse(BaseResponse):
    id: int
    ig_id: int
    user_id: str
    created_at: datetime
    user: UserSummaryResponse


class PigWebsiteResponse(BaseResponse):
    id: int
    pig_id: int
    label: str
    url: str
    sort_order: int
    created_at: datetime
    updated_at: datetime


class PigResponse(BaseResponse):
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
    is_rolling_admission: RollingAdmission
    created_at: datetime
    updated_at: datetime
    owner_user: UserSummaryResponse
    members: list[PigMemberResponse]
    websites: list[PigWebsiteResponse]
