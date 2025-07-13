from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.db import SessionDep
from src.model import SIG, SCSCGlobalStatus, SIGMember, SCSCStatus
from src.util import get_user_role_level, send_discord_bot_request_no_reply

from .article import BodyCreateArticle, create_article_ctrl
from .scsc import ctrl_status_available


class BodyCreateSIG(BaseModel):
    title: str
    description: str
    content: str


async def create_sig_ctrl(session: SessionDep, body: BodyCreateSIG, user_id: str, user_discord_id: int, scsc_global_status: SCSCGlobalStatus) -> SIG:
    if scsc_global_status.status not in ctrl_status_available.create_sigpig: raise HTTPException(400, f"cannot create sig when sig global status is not in {ctrl_status_available.create_sigpig}")

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
        raise HTTPException(409, detail="unique field already exists")
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
    await send_discord_bot_request_no_reply(action_code=4001, body={'sig_name': body.title, 'user_id_list': [user_discord_id]})
    return sig


class BodyUpdateSIG(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    status: Optional[SCSCStatus] = None


async def update_sig_ctrl(session: SessionDep, id: int, body: BodyUpdateSIG, user_id: str, is_executive: bool) -> None:
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="sig not found")
    if not is_executive and sig.owner != user_id: raise HTTPException(status_code=403, detail="cannot update sig of other")

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
        if not is_executive: raise HTTPException(403, detail="Only executive and above can update status")
        sig.status = body.status

    session.add(sig)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="unique field already exists")
    return
