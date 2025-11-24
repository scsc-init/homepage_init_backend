from datetime import datetime

from .base import BaseResponse


class BoardResponse(BaseResponse):
    id: int
    name: str
    description: str
    writing_permission_level: int
    reading_permission_level: int
    created_at: datetime
    updated_at: datetime
