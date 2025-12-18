from datetime import datetime

from .base import BaseResponse


class CommentResponse(BaseResponse):
    id: int
    content: str
    author_id: str
    article_id: int
    parent_id: int | None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
