from datetime import datetime
from typing import Optional

from src.model import UserStatus

from .base import BaseResponse


class UserResponse(BaseResponse):
    id: str
    email: str
    name: str
    phone: str
    student_id: str
    role: int
    major_id: int
    status: UserStatus
    discord_id: Optional[int] = None
    discord_name: Optional[str] = None
    profile_picture: Optional[str] = None
    profile_picture_is_url: bool
    last_login: datetime
    created_at: datetime
    updated_at: datetime


class StandbyReqTblRepository(DAO[StandbyReqTbl, str]):
    standby_user_id: str
    user_name: str
    deposit_name: str
    is_checked: bool
    deposit_time: Optional[datetime] = None
