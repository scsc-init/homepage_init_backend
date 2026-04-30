from datetime import datetime

from .attachment import AttachmentResponse
from .base import BaseResponse


class ArticleResponse(BaseResponse):
    id: int
    title: str
    author_id: str
    board_id: int
    created_at: datetime
    updated_at: datetime
    content: str | None = None
    attachments: list[AttachmentResponse] = []
