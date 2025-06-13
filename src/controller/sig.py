from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.db import SessionDep
from src.model import SIG, SIGGlobalStatus, SIGMember, SIGStatus, User
from src.util import is_valid_semester, is_valid_year

from .article import BodyCreateArticle, create_article_controller


class BodyCreateSIG(BaseModel):
    title: str
    description: str
    content: str
    year: int
    semester: int


async def create_sig_controller(body: BodyCreateSIG, session: SessionDep, current_user: User, sig_global_status: SIGGlobalStatus) -> SIG:
    if sig_global_status.status != SIGStatus.surveying: raise HTTPException(400, "cannot create sig when sig global status is not surveying")
    if not is_valid_year(body.year): raise HTTPException(422, detail="invalid year")
    if not is_valid_semester(body.semester): raise HTTPException(422, detail="invalid semester")

    sig_article = await create_article_controller(
        BodyCreateArticle(title=body.title, content=body.content, board_id=1),
        session=session,
        current_user=None
    )

    sig = SIG(
        title=body.title,
        description=body.description,
        content_id=sig_article.id,
        year=body.year,
        semester=body.semester,
        owner=current_user.id,
        status=SIGStatus.surveying
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
        user_id=current_user.id,
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
    status: Optional[SIGStatus] = None
    year: Optional[int] = None
    semester: Optional[int] = None


async def update_sig_controller(id: int, body: BodyUpdateSIG, session: SessionDep, current_user: Optional[User]) -> None:
    """
    If current_user is None: role level will be treated as executive.

    The controller can raise HTTPException.
    """

    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="sig not found")
    if current_user and sig.owner != current_user.id: raise HTTPException(
        status_code=403, detail="cannot update sig of other")
    if body.year and not is_valid_year(body.year): raise HTTPException(422, detail="invalid year")
    if body.semester and not is_valid_semester(body.semester): raise HTTPException(422, detail="invalid semester")

    if body.title: sig.title = body.title
    if body.description: sig.description = body.description
    if body.content:
        sig_article = await create_article_controller(
            BodyCreateArticle(title=sig.title, content=body.content, board_id=1),
            session=session,
            current_user=None
        )
        sig.content_id = sig_article.id
    if body.status:
        if current_user: raise HTTPException(403, detail="Only executive and above can update status")
        sig.status = body.status
    if body.year: sig.year = body.year
    if body.semester: sig.semester = body.semester

    session.add(sig)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="unique field already exists")
    return
