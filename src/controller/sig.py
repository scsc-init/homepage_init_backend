from typing import Optional
import logging

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.db import SessionDep
from src.model import SIG, SCSCGlobalStatus, SIGMember, SCSCStatus
from src.util import get_user_role_level, send_discord_bot_request_no_reply, send_discord_bot_request

from .article import BodyCreateArticle, create_article_ctrl
from .scsc import ctrl_status_available

logger = logging.getLogger("app")

class BodyCreateSIG(BaseModel):
    title: str
    description: str
    content: str


async def create_sig_ctrl(session: SessionDep, body: BodyCreateSIG, user_id: str, user_discord_id: Optional[int], scsc_global_status: SCSCGlobalStatus) -> SIG:
    if scsc_global_status.status not in ctrl_status_available.create_sigpig: raise HTTPException(400, f"SCSC 전역 상태가 {ctrl_status_available.create_sigpig}일 때만 시그/피그를 생성할 수 있습니다")

    sig_article = await create_article_ctrl(
        session,
        BodyCreateArticle(title=body.title, content=body.content, board_id=1),
        user_id,
        get_user_role_level('president')
    )

    sig = SIG(
        title=body.title,
        description=body.description,
        content_id=sig_article.id,
        year=scsc_global_status.year,
        semester=scsc_global_status.semester,
        owner=user_id,
        status=scsc_global_status.status
    )
    session.add(sig)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")
    session.refresh(sig)

    if sig.id is None: raise HTTPException(503, detail="sig primary key does not exist")
    sig_member = SIGMember(
        ig_id=sig.id,
        user_id=user_id,
        status=sig.status
    )
    session.add(sig_member)
    session.commit()
    session.refresh(sig)
    if user_discord_id: await send_discord_bot_request_no_reply(action_code=4001, body={'sig_name': body.title, 'user_id_list': [user_discord_id], "sig_description": sig.description})
    logger.info(f'info_type=sig_created ; sig_id={sig.id} ; title={body.title} ; owner_id={user_id} ; year={sig.year} ; semester={sig.semester}')
    return sig


class BodyUpdateSIG(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    status: Optional[SCSCStatus] = None


async def update_sig_ctrl(session: SessionDep, id: int, body: BodyUpdateSIG, user_id: str, is_executive: bool) -> None:
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    if not is_executive and sig.owner != user_id: raise HTTPException(status_code=403, detail="타인의 시그/피그를 변경할 수 없습니다")
    old_title = sig.title
    if body.title: sig.title = body.title
    if body.description: sig.description = body.description
    if body.content:
        sig_article = await create_article_ctrl(
            session,
            BodyCreateArticle(title=sig.title, content=body.content, board_id=1),
            user_id,
            get_user_role_level('president')
        )
        sig.content_id = sig_article.id
    if body.status:
        if not is_executive: raise HTTPException(403, detail="관리자 이상의 권한이 필요합니다")
        sig.status = body.status

    session.add(sig)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")
    session.refresh(sig)
    response = await send_discord_bot_request(action_code=1004, body={"channel_name": old_title})
    if response is not None:
        channel_id = response['channel_id']
        bot_body = {"channel_id": channel_id}
        if body.title: bot_body['new_channel_name'] = body.title
        if body.description: bot_body['new_topic'] = body.description
        await send_discord_bot_request_no_reply(action_code=3007, body=bot_body)
    logger.info(f'info_type=sig_updated ; sig_id={id} ; title={body.title} ; revisioner_id={user_id} ; year={sig.year} ; semester={sig.semester}')
    return
