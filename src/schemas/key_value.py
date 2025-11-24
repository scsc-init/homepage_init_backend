from typing import Optional

from .base import BaseResponse


class KvResponse(BaseResponse):
    key: str
    value: Optional[str]
