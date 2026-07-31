from datetime import datetime
from typing import Optional

from .base import BaseResponse
from .major import MajorResponse


class UserResponse(BaseResponse):
    id: str
    email: str
    name: str
    kakao_name: Optional[str] = None
    phone: str
    student_id: Optional[str] = None
    role: int
    major_id: Optional[int] = None
    is_active: bool
    is_banned: bool
    discord_id: Optional[int] = None
    discord_name: Optional[str] = None
    profile_picture: Optional[str] = None
    profile_picture_is_url: bool
    last_login: datetime
    created_at: datetime
    updated_at: datetime


class UserSummaryResponse(BaseResponse):
    id: str
    name: str
    kakao_name: Optional[str] = None
    email: str
    major_id: Optional[int] = None
    role: int
    is_active: bool
    is_banned: bool
    major: Optional[MajorResponse] = None


class PublicUserResponse(BaseResponse):
    id: str
    email: str
    name: str
    role: int
    is_active: bool
    is_banned: bool
    profile_picture: Optional[str] = None
    profile_picture_is_url: bool


class StandbyReqTblResponse(BaseResponse):
    standby_user_id: str
    user_name: str
    deposit_name: str
    is_checked: bool
    deposit_time: Optional[datetime] = None


class OldboyApplicantResponse(BaseResponse):
    id: str
    processed: bool
    created_at: datetime
