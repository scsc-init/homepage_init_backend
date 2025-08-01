from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.db import SessionDep
from src.model import PIG, SCSCGlobalStatus, PIGMember, SCSCStatus
from src.util import get_user_role_level, send_discord_bot_request_no_reply

from .article import BodyCreateArticle, create_article_ctrl
from .scsc import ctrl_status_available


class BodyCreatePIG(BaseModel):
    title: str
    description: str
    content: str


async def create_pig_ctrl(session: SessionDep, body: BodyCreatePIG, user_id: str, user_discord_id: Optional[int], scsc_global_status: SCSCGlobalStatus) -> PIG:
    if scsc_global_status.status not in ctrl_status_available.create_sigpig: raise HTTPException(400, f"SCSC 전역 상태가 {ctrl_status_available.create_sigpig}일 때만 시그/피그를 생성할 수 있습니다")

    pig_article = await create_article_ctrl(
        session,
        BodyCreateArticle(title=body.title, content=body.content, board_id=1),
        user_id,
        get_user_role_level('president')
    )

    pig = PIG(
        title=body.title,
        description=body.description,
        content_id=pig_article.id,
        year=scsc_global_status.year,
        semester=scsc_global_status.semester,
        owner=user_id,
        status=scsc_global_status.status
    )
    session.add(pig)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")
    session.refresh(pig)

    if pig.id is None: raise HTTPException(503, detail="pig primary key does not exist")
    pig_member = PIGMember(
        ig_id=pig.id,
        user_id=user_id,
        status=pig.status
    )
    session.add(pig_member)
    session.commit()
    session.refresh(pig)
    if user_discord_id: await send_discord_bot_request_no_reply(action_code=4003, body={'pig_name': body.title, 'user_id_list': ([user_discord_id])})
    return pig


class BodyUpdatePIG(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    status: Optional[SCSCStatus] = None


async def update_pig_ctrl(session: SessionDep, id: int, body: BodyUpdatePIG, user_id: str, is_executive: bool) -> None:
    pig = session.get(PIG, id)
    if not pig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    if not is_executive and pig.owner != user_id: raise HTTPException(status_code=403, detail="타인의 시그/피그를 변경할 수 없습니다")

    if body.title: pig.title = body.title
    if body.description: pig.description = body.description
    if body.content:
        pig_article = await create_article_ctrl(
            session,
            BodyCreateArticle(title=pig.title, content=body.content, board_id=1),
            user_id,
            get_user_role_level('president')
        )
        pig.content_id = pig_article.id
    if body.status:
        if not is_executive: raise HTTPException(403, detail="관리자 이상의 권한이 필요합니다")
        pig.status = body.status

    session.add(pig)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")
    return
