from datetime import datetime

from src.model import SCSCStatus

from .base import BaseResponse


class SCSCGlobalStatusResponse(BaseResponse):
    id: int
    status: SCSCStatus
    year: int
    semester: int
    updated_at: datetime
