from datetime import datetime

from .base import BaseResponse


class WHTMLMetadataResponse(BaseResponse):
    name: str
    size: int
    creator: str | None = None
    created_at: datetime
    updated_at: datetime


class WHTMLMetadataWithCreatorResponse(WHTMLMetadataResponse):
    creator_name: str | None = None
