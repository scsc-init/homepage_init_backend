from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.db import SessionDep
from src.model import PIG, PIGGlobalStatus, PIGMember, PIGStatus, User
from src.util import is_valid_semester, is_valid_year

from .article import BodyCreateArticle, create_article_controller


class BodyCreatePIG(BaseModel):
    title: str
    description: str
    content: str
    year: int
    semester: int


async def create_pig_controller(body: BodyCreatePIG, session: SessionDep, current_user: User, pig_global_status: PIGGlobalStatus) -> PIG:
    if pig_global_status.status != PIGStatus.surveying: raise HTTPException(400, "cannot create pig when pig global status is not surveying")
    if not is_valid_year(body.year): raise HTTPException(422, detail="invalid year")
    if not is_valid_semester(body.semester): raise HTTPException(422, detail="invalid semester")

    pig_article = await create_article_controller(
        BodyCreateArticle(title=body.title, content=body.content, board_id=1),
        session=session,
        current_user=None
    )

    pig = PIG(
        title=body.title,
        description=body.description,
        content_id=pig_article.id,
        year=body.year,
        semester=body.semester,
        owner=current_user.id,
        status=PIGStatus.surveying
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
        user_id=current_user.id,
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
    status: Optional[PIGStatus] = None
    year: Optional[int] = None
    semester: Optional[int] = None


async def update_pig_controller(id: int, body: BodyUpdatePIG, session: SessionDep, current_user: Optional[User]) -> None:
    """
    If current_user is None: role level will be treated as executive.

    The controller can raise HTTPException.
    """

    pig = session.get(PIG, id)
    if not pig: raise HTTPException(404, detail="pig not found")
    if current_user and pig.owner != current_user.id: raise HTTPException(
        status_code=403, detail="cannot update pig of other")
    if body.year and not is_valid_year(body.year): raise HTTPException(422, detail="invalid year")
    if body.semester and not is_valid_semester(body.semester): raise HTTPException(422, detail="invalid semester")

    if body.title: pig.title = body.title
    if body.description: pig.description = body.description
    if body.content:
        pig_article = await create_article_controller(
            BodyCreateArticle(title=pig.title, content=body.content, board_id=1),
            session=session,
            current_user=None
        )
        pig.content_id = pig_article.id
    if body.status:
        if current_user: raise HTTPException(403, detail="Only executive and above can update status")
        pig.status = body.status
    if body.year: pig.year = body.year
    if body.semester: pig.semester = body.semester

    session.add(pig)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="unique field already exists")
    return
