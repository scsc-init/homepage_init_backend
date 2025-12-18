from .base import BaseResponse


class MajorResponse(BaseResponse):
    id: int
    college: str
    major_name: str
