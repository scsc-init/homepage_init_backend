from datetime import datetime
from typing import Any, Optional, Sequence

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
    owner_user: Optional[UserSummaryResponse] = None
    members: Optional[list[SigMemberResponse]] = None
    websites: list[SigWebsiteResponse]
    tags: list[TagResponse]

    @classmethod
    def model_validate_visible(
        cls, sig: Any, *, include_members: bool
    ) -> "SigResponse":
        """구성원 정보는 로그인한 사용자에게만 응답한다.

        owner_user와 members는 이름/이메일/카카오 이름 등 개인정보를 담고 있어
        비로그인 요청에서는 None으로 응답한다. 시그 자체의 정보(제목, 설명,
        태그, 웹사이트 등)는 그대로 공개된다.
        """
        response = cls.model_validate(sig)
        if not include_members:
            response.owner_user = None
            response.members = None
        return response

    @classmethod
    def model_validate_visible_list(
        cls, sigs: Sequence[Any], *, include_members: bool
    ) -> Sequence["SigResponse"]:
        return [
            cls.model_validate_visible(sig, include_members=include_members)
            for sig in sigs
        ]


class SigTagResponse(BaseResponse):
    id: int
    sig_id: int
    tag_id: int
    created_at: datetime
