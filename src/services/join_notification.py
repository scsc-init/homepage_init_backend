from datetime import datetime
from typing import Optional

from src.core import logger
from src.model import User
from src.repositories.user import UserRepository
from src.util import utcnow

from .sms import send_sms


async def notify_ig_owner_join_sms(
    *,
    ig_type: str,
    ig_id: int,
    ig_title: str,
    owner_id: str,
    joined_user: User,
    applied_at: Optional[datetime],
    user_repository: UserRepository,
) -> None:
    owner = user_repository.get_by_id(owner_id)
    if owner is None:
        logger.error(
            f"err_type={ig_type}_join_sms ; err_code=404 ; msg=owner not found ; ig_id={ig_id} ; owner_id={owner_id} ; joined_user_id={joined_user.id}"
        )
        return

    applied_at_text = (applied_at or utcnow()).strftime("%Y-%m-%d %H:%M:%S UTC")
    content = (
        f"[SCSC] {joined_user.name}({joined_user.id})님이 "
        f"{ig_title}({ig_type.upper()})에 {applied_at_text} 가입 신청했습니다."
    )

    try:
        await send_sms(to=owner.phone, content=content)
        logger.info(
            f"info_type={ig_type}_join_sms_queued ; ig_id={ig_id} ; owner_id={owner.id} ; joined_user_id={joined_user.id}"
        )
    except Exception as exc:
        logger.error(
            f"err_type={ig_type}_join_sms ; err_code=500 ; ig_id={ig_id} ; owner_id={owner.id} ; joined_user_id={joined_user.id} ; msg={exc}",
            exc_info=True,
        )
