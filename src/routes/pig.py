from typing import Optional, Sequence

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.auth import get_current_user
from src.db import SessionDep
from src.model import PIG, PIGMember, PIGStatus, User, UserRole
from src.util import is_valid_semester, is_valid_year

pig_router = APIRouter(tags=['pig'])


class BodyCreatePIG(BaseModel):
    title: str
    description: str
    content_src: str
    year: int
    semester: int


@pig_router.post('/pig/create', status_code=201)
async def create_pig(body: BodyCreatePIG, session: SessionDep, current_user: User = Depends(get_current_user)) -> PIG:
    if not is_valid_year(body.year):
        raise HTTPException(422, detail="invalid year")
    if not is_valid_semester(body.semester):
        raise HTTPException(422, detail="invalid semester")

    pig = PIG(
        title=body.title,
        description=body.description,
        content_src=body.content_src,
        year=body.year,
        semester=body.semester,
        owner=current_user.id
    )
    session.add(pig)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail=f"unique field already exists")
    session.refresh(pig)
    if pig.id is None:
        raise HTTPException(
            status_code=503, detail=f"pig primary key does not exist")
    pig_member = PIGMember(
        ig_id=pig.id,
        user_id=current_user.id
    )
    session.add(pig_member)
    session.commit()
    session.refresh(pig)
    return pig


@pig_router.get('/pig/{id}')
async def get_pig_by_id(id: int, session: SessionDep) -> PIG:
    pig = session.get(PIG, id)
    if not pig:
        raise HTTPException(status_code=404, detail="pig not found")
    return pig


@pig_router.get('/pigs')
async def get_all_pigs(session: SessionDep) -> Sequence[PIG]:
    return session.exec(select(PIG)).all()


class BodyUpdateMyPIG(BaseModel):
    title: str
    description: str
    content_src: str
    year: int
    semester: int


@pig_router.post('/pig/{id}/update', status_code=204)
async def update_my_pig(id: int, body: BodyUpdateMyPIG, session: SessionDep, current_user: User = Depends(get_current_user)) -> None:
    pig = session.get(PIG, id)
    if not pig:
        raise HTTPException(status_code=404, detail="pig not found")
    if pig.owner != current_user.id:
        raise HTTPException(
            status_code=403, detail="cannot update pig of other")
    if not is_valid_year(body.year):
        raise HTTPException(422, detail="invalid year")
    if not is_valid_semester(body.semester):
        raise HTTPException(422, detail="invalid semester")

    pig.title = body.title
    pig.description = body.description
    pig.content_src = body.content_src
    pig.year = body.year
    pig.semester = body.semester
    session.add(pig)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail=f"unique field already exists")
    return


@pig_router.post('/pig/{id}/delete', status_code=204)
async def delete_my_pig(id: int, session: SessionDep, current_user: User = Depends(get_current_user)) -> None:
    pig = session.get(PIG, id)
    if not pig:
        raise HTTPException(status_code=404, detail="pig not found")
    if pig.owner != current_user.id:
        raise HTTPException(
            status_code=403, detail="cannot delete pig of other")
    session.delete(pig)
    session.commit()
    return


class BodyUpdatePIG(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content_src: Optional[str] = None
    status: Optional[PIGStatus] = None
    year: Optional[int] = None
    semester: Optional[int] = None


@pig_router.post('/executive/pig/{id}/update', status_code=204)
async def update_pig(id: int, body: BodyUpdatePIG, session: SessionDep) -> None:
    pig = session.get(PIG, id)
    if pig is None:
        raise HTTPException(404, detail="no pig exists")
    if body.title:
        pig.title = body.title
    if body.description:
        pig.description = body.description
    if body.content_src:
        pig.content_src = body.content_src
    if body.status:
        pig.status = body.status
    if body.year:
        if not is_valid_year(body.year):
            raise HTTPException(422, detail="invalid year")
        pig.year = body.year
    if body.semester:
        if not is_valid_semester(body.semester):
            raise HTTPException(422, detail="invalid semester")
        pig.semester = body.semester
    session.add(pig)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail=f"unique field already exists")
    return


@pig_router.post('/executive/pig/{id}/delete', status_code=204)
async def delete_pig(id: int, session: SessionDep) -> None:
    pig = session.get(PIG, id)
    if not pig:
        raise HTTPException(status_code=404, detail="pig not found")
    session.delete(pig)
    session.commit()
    return


class BodyHandoverPIG(BaseModel):
    new_owner: str


@pig_router.post('/pig/{id}/handover', status_code=204)
async def handover_pig(id: int, body: BodyHandoverPIG, session: SessionDep, current_user: User = Depends(get_current_user)) -> None:
    pig = session.get(PIG, id)
    if pig is None:
        raise HTTPException(404, detail="no pig exists")
    user = session.exec(select(PIGMember).where(PIGMember.ig_id == id).where(
        PIGMember.user_id == body.new_owner)).first()
    if not user:
        raise HTTPException(
            status_code=404, detail="new_owner should be a member of the pig")
    if current_user.role < UserRole.executive and current_user.id != pig.owner:
        raise HTTPException(
            403, "handover can be executed only by executive or owner of the pig")
    pig.owner = body.new_owner
    session.add(pig)
    session.commit()
    return


@pig_router.get('/pig/{id}/members')
async def get_pig_members(id: int, session: SessionDep) -> Sequence[PIGMember]:
    return session.exec(select(PIGMember).where(PIGMember.ig_id == id)).all()


@pig_router.post('/pig/{id}/member/join', status_code=204)
async def join_pig(id: int, session: SessionDep, current_user: User = Depends(get_current_user)):
    pig = session.get(PIG, id)
    if not pig:
        raise HTTPException(status_code=404, detail="pig not found")
    pig_member = PIGMember(
        ig_id=id,
        user_id=current_user.id
    )
    session.add(pig_member)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail=f"unique field already exists")
    return


@pig_router.post('/pig/{id}/member/leave', status_code=204)
async def leave_pig(id: int, session: SessionDep, current_user: User = Depends(get_current_user)):
    pig = session.get(PIG, id)
    if not pig:
        raise HTTPException(status_code=404, detail="pig not found")
    if pig.owner == current_user.id:
        raise HTTPException(
            status_code=409, detail="pig owner cannot leave the pig")
    pig_member = session.exec(select(PIGMember).where(
        PIGMember.ig_id == id).where(PIGMember.user_id == current_user.id)).first()
    if not pig_member:
        raise HTTPException(status_code=404, detail="pig member not found")
    session.delete(pig_member)
    session.commit()
    return


class BodyExecutiveJoinPIG(BaseModel):
    user_id: str


@pig_router.post('/executive/pig/{id}/member/join', status_code=204)
async def executive_join_pig(id: int, body: BodyExecutiveJoinPIG, session: SessionDep):
    pig = session.get(PIG, id)
    if not pig:
        raise HTTPException(status_code=404, detail="pig not found")
    user = session.get(User, body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    pig_member = PIGMember(
        ig_id=id,
        user_id=body.user_id
    )
    session.add(pig_member)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail=f"unique field already exists")
    return


class BodyExecutiveLeavePIG(BaseModel):
    user_id: str


@pig_router.post('/executive/pig/{id}/member/leave', status_code=204)
async def executive_leave_pig(id: int, body: BodyExecutiveLeavePIG, session: SessionDep):
    pig = session.get(PIG, id)
    if not pig:
        raise HTTPException(status_code=404, detail="pig not found")
    user = session.get(User, body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    if pig.owner == user.id:
        raise HTTPException(
            status_code=409, detail="pig owner cannot leave the pig")
    pig_member = session.exec(select(PIGMember).where(
        PIGMember.ig_id == id).where(PIGMember.user_id == body.user_id)).first()
    if not pig_member:
        raise HTTPException(status_code=404, detail="pig member not found")
    session.delete(pig_member)
    session.commit()
    return
