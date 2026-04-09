from datetime import datetime

from src.model import SCSCStatus
from src.model.sig import RollingAdmission

from .article import ArticleResponse
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


class SigWebsiteResponse(BaseResponse):
    id: int
    sig_id: int
    label: str
    url: str
    sort_order: int
    created_at: datetime
    updated_at: datetime


class SigResponse(BaseResponse):
    id: int
    title: str
    description: str
    content: ArticleResponse
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
    members: list[SigMemberResponse]
    websites: list[SigWebsiteResponse]
    tags: list[TagResponse]


class SigTagResponse(BaseResponse):
    id: int
    sig_id: int
    tag_id: int
    created_at: datetime
