from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.db import SessionDep
from src.model import SIG, SCSCGlobalStatus, SIGMember, SCSCStatus
from src.util import is_valid_semester, is_valid_year, get_user_role_level

from .article import BodyCreateArticle, create_article_controller


class BodyCreateSIG(BaseModel):
    title: str
    description: str
    content: str
    year: int
    semester: int


async def create_sig_controller(session: SessionDep, body: BodyCreateSIG, user_id: str, scsc_global_status: SCSCGlobalStatus) -> SIG:
    if scsc_global_status.status != SCSCStatus.surveying: raise HTTPException(400, "cannot create sig when sig global status is not surveying")
    if not is_valid_year(body.year): raise HTTPException(422, detail="invalid year")
    if not is_valid_semester(body.semester): raise HTTPException(422, detail="invalid semester")

    sig_article = await create_article_controller(
        session,
        BodyCreateArticle(title=body.title, content=body.content, board_id=1),
        user_id,
        get_user_role_level('president')
    )

    sig = SIG(
        title=body.title,
        description=body.description,
        content_id=sig_article.id,
        year=body.year,
        semester=body.semester,
        owner=user_id,
        status=SCSCStatus.surveying
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
    return sig


class BodyUpdateSIG(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    status: Optional[SCSCStatus] = None
    year: Optional[int] = None
    semester: Optional[int] = None


async def update_sig_controller(session: SessionDep, id: int, body: BodyUpdateSIG, user_id: str, is_executive: bool) -> None:
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="sig not found")
    if not is_executive and sig.owner != user_id: raise HTTPException(status_code=403, detail="cannot update sig of other")
    if body.year and not is_valid_year(body.year): raise HTTPException(422, detail="invalid year")
    if body.semester and not is_valid_semester(body.semester): raise HTTPException(422, detail="invalid semester")

    if body.title: sig.title = body.title
    if body.description: sig.description = body.description
    if body.content:
        sig_article = await create_article_controller(
            session,
            BodyCreateArticle(title=sig.title, content=body.content, board_id=1),
            user_id,
            get_user_role_level('president')
        )
        sig.content_id = sig_article.id
    if body.status:
        if not is_executive: raise HTTPException(403, detail="Only executive and above can update status")
        sig.status = body.status
    if body.year: sig.year = body.year
    if body.semester: sig.semester = body.semester

    session.add(sig)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="unique field already exists")
    return
