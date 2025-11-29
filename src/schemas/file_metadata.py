from datetime import datetime

from .base import BaseResponse


class FileMetadataResponse(BaseResponse):
    id: str
    original_filename: str
    size: int
    mime_type: str
    owner: str | None = None
    created_at: datetime
