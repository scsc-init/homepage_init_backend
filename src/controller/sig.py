import logging
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.db import SessionDep
from src.model import SIG, SCSCGlobalStatus, SCSCStatus, SIGMember, User
from src.util import get_user_role_level, send_discord_bot_request_no_reply

from .article import BodyCreateArticle, create_article_ctrl
from .scsc import ctrl_status_available

logger = logging.getLogger("app")


class BodyCreateSIG(BaseModel):
    title: str
    description: str
    content: str
    is_rolling_admission: bool = False


async def create_sig_ctrl(
    session: SessionDep,
    body: BodyCreateSIG,
    user_id: str,
    user_discord_id: Optional[int],
    scsc_global_status: SCSCGlobalStatus,
) -> SIG:
    if scsc_global_status.status not in ctrl_status_available.create_sigpig:
        raise HTTPException(
            400,
            f"SCSC 전역 상태가 {ctrl_status_available.create_sigpig}일 때만 시그/피그를 생성할 수 있습니다",
        )

    sig_article = await create_article_ctrl(
        session,
        BodyCreateArticle(title=body.title, content=body.content, board_id=1),
        user_id,
        get_user_role_level("president"),
    )

    sig = SIG(
        title=body.title,
        description=body.description,
        content_id=sig_article.id,
        year=scsc_global_status.year,
        semester=scsc_global_status.semester,
        owner=user_id,
        status=scsc_global_status.status,
        is_rolling_admission=body.is_rolling_admission,
    )
    session.add(sig)
    try:
        session.flush()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")
    session.refresh(sig)

    if sig.id is None:
        raise HTTPException(503, detail="sig primary key does not exist")
    sig_member = SIGMember(ig_id=sig.id, user_id=user_id)
    session.add(sig_member)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="시그장 자동 가입 중 중복 오류가 발생했습니다")
    session.refresh(sig)
    if user_discord_id:
        await send_discord_bot_request_no_reply(
            action_code=4001,
            body={
                "sig_name": sig.title,
                "user_id_list": [user_discord_id],
                "sig_description": sig.description,
            },
        )
    logger.info(
        f"info_type=sig_created ; sig_id={sig.id} ; title={sig.title} ; owner_id={user_id} ; year={sig.year} ; semester={sig.semester} ; is_rolling_admission={sig.is_rolling_admission}"
    )
    return sig


class BodyUpdateSIG(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    status: Optional[SCSCStatus] = None
    should_extend: Optional[bool] = None
    is_rolling_admission: Optional[bool] = None


async def update_sig_ctrl(
    session: SessionDep, id: int, body: BodyUpdateSIG, user_id: str, is_executive: bool
) -> None:
    sig = session.get(SIG, id)
    if not sig:
        raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    if not is_executive and sig.owner != user_id:
        raise HTTPException(
            status_code=403, detail="타인의 시그/피그를 변경할 수 없습니다"
        )
    old_title = sig.title
    if body.title:
        sig.title = body.title
    if body.description:
        sig.description = body.description
    if body.content:
        sig_article = await create_article_ctrl(
            session,
            BodyCreateArticle(title=sig.title, content=body.content, board_id=1),
            user_id,
            get_user_role_level("president"),
        )
        sig.content_id = sig_article.id
    if body.status:
        if not is_executive:
            raise HTTPException(403, detail="관리자 이상의 권한이 필요합니다")
        sig.status = body.status
    if body.should_extend is not None:
        sig.should_extend = body.should_extend
    if body.is_rolling_admission is not None:
        sig.is_rolling_admission = body.is_rolling_admission

    session.add(sig)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")
    session.refresh(sig)

    bot_body = {}
    bot_body["sig_name"] = old_title
    if body.title:
        bot_body["new_sig_name"] = body.title
    if body.description:
        bot_body["new_topic"] = body.description
    if len(bot_body) > 1:
        await send_discord_bot_request_no_reply(action_code=4005, body=bot_body)

    logger.info(
        f"info_type=sig_updated ; sig_id={id} ; title={sig.title} ; revisioner_id={user_id} ; year={sig.year} ; semester={sig.semester} ; is_rolling_admission={sig.is_rolling_admission}"
    )
    return


def handover_sig_ctrl(
    session: SessionDep, sig: SIG, new_owner_id: str, executor_id: str, is_forced: bool
) -> SIG:
    if sig.owner == new_owner_id:
        raise HTTPException(
            status_code=400,
            detail="새로운 시그/피그장은 현재 시그/피그장과 달라야 합니다",
        )

    new_owner_user = session.get(User, new_owner_id)
    if not new_owner_user:
        raise HTTPException(
            status_code=404, detail="새로운 시그/피그장에 해당하는 사용자가 없습니다"
        )

    member = session.exec(
        select(SIGMember)
        .where(SIGMember.ig_id == sig.id)
        .where(SIGMember.user_id == new_owner_id)
    ).first()
    if not member:
        raise HTTPException(
            status_code=404,
            detail="새로운 시그/피그장은 해당 시그/피그의 구성원이어야 합니다",
        )

    old_owner = sig.owner
    sig.owner = new_owner_id
    session.add(sig)
    session.commit()
    session.refresh(sig)

    handover_type = "forced" if is_forced else "voluntary"
    logger.info(
        f"info_type=sig_handover ; handover_type={handover_type} ; sig_id={sig.id} ; title={sig.title} ; "
        f"executor_id={executor_id} ; old_owner_id={old_owner} ; new_owner_id={new_owner_id} ; "
        f"year={sig.year} ; semester={sig.semester}"
    )

    return sig
