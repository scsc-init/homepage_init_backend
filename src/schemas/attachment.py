from .base import BaseResponse


class AttachmentResponse(BaseResponse):
    id: int
    article_id: int
    file_id: str

    class Config:
        from_attributes = True
