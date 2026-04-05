from datetime import datetime

from .base import BaseResponse
from src.model import BoardType


class BoardResponse(BaseResponse):
    id: int
    name: str
    description: str
    writing_permission_level: int
    reading_permission_level: int
    board_type: BoardType
    created_at: datetime
    updated_at: datetime
