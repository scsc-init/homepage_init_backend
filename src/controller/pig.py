from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.db import SessionDep
from src.model import PIG, SCSCGlobalStatus, PIGMember, SCSCStatus
from src.util import get_user_role_level

from .article import BodyCreateArticle, create_article_ctrl
from .scsc import ctrl_status_available


class BodyCreatePIG(BaseModel):
    title: str
    description: str
    content: str


async def create_pig_ctrl(session: SessionDep, body: BodyCreatePIG, user_id: str, scsc_global_status: SCSCGlobalStatus) -> PIG:
    if scsc_global_status.status not in ctrl_status_available.create_sigpig: raise HTTPException(400, f"cannot create pig when pig global status is not in {ctrl_status_available.create_sigpig}")

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
        status=SCSCStatus.surveying
    )
    session.add(pig)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="unique field already exists")
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
    return pig


class BodyUpdatePIG(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    status: Optional[SCSCStatus] = None


async def update_pig_ctrl(session: SessionDep, id: int, body: BodyUpdatePIG, user_id: str, is_executive: bool) -> None:
    pig = session.get(PIG, id)
    if not pig: raise HTTPException(404, detail="pig not found")
    if not is_executive and pig.owner != user_id: raise HTTPException(status_code=403, detail="cannot update pig of other")

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
        if not is_executive: raise HTTPException(403, detail="Only executive and above can update status")
        pig.status = body.status

    session.add(pig)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="unique field already exists")
    return
