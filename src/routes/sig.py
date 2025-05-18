from typing import Optional, Sequence

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.auth import get_current_user
from src.db import SessionDep
from src.model import SIG, SIGMember, SIGStatus, User
from src.util import is_valid_semester, is_valid_year

sig_router = APIRouter(tags=['sig'])


class BodyCreateSIG(BaseModel):
    title: str
    description: str
    content_src: str
    year: int
    semester: int


@sig_router.post('/sig/create', status_code=201)
async def create_sig(body: BodyCreateSIG, session: SessionDep, current_user: User = Depends(get_current_user)) -> SIG:
    if not is_valid_year(body.year):
        raise HTTPException(422, detail="invalid year")
    if not is_valid_semester(body.semester):
        raise HTTPException(422, detail="invalid semester")

    sig = SIG(
        title=body.title,
        description=body.description,
        content_src=body.content_src,
        year=body.year,
        semester=body.semester,
        owner=current_user.id
    )
    session.add(sig)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail=f"unique field already exists")
    session.refresh(sig)
    if sig.id is None:
        raise HTTPException(
            status_code=503, detail=f"sig primary key does not exist")
    sig_member = SIGMember(
        ig_id=sig.id,
        user_id=current_user.id
    )
    session.add(sig_member)
    session.commit()
    session.refresh(sig)
    return sig


@sig_router.get('/sig/{id}')
async def get_sig_by_id(id: int, session: SessionDep) -> SIG:
    sig = session.get(SIG, id)
    if not sig:
        raise HTTPException(status_code=404, detail="sig not found")
    return sig


@sig_router.get('/sigs')
async def get_all_sigs(session: SessionDep) -> Sequence[SIG]:
    return session.exec(select(SIG)).all()


class BodyUpdateMySIG(BaseModel):
    title: str
    description: str
    content_src: str
    year: int
    semester: int


@sig_router.post('/sig/{id}/update', status_code=204)
async def update_my_sig(id: int, body: BodyUpdateMySIG, session: SessionDep, current_user: User = Depends(get_current_user)) -> None:
    sig = session.get(SIG, id)
    if not sig:
        raise HTTPException(status_code=404, detail="sig not found")
    if sig.owner != current_user.id:
        raise HTTPException(
            status_code=403, detail="cannot update sig of other")
    if not is_valid_year(body.year):
        raise HTTPException(422, detail="invalid year")
    if not is_valid_semester(body.semester):
        raise HTTPException(422, detail="invalid semester")

    sig.title = body.title
    sig.description = body.description
    sig.content_src = body.content_src
    sig.year = body.year
    sig.semester = body.semester
    session.add(sig)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail=f"unique field already exists")
    return


@sig_router.post('/sig/{id}/delete', status_code=204)
async def delete_my_sig(id: int, session: SessionDep, current_user: User = Depends(get_current_user)) -> None:
    sig = session.get(SIG, id)
    if not sig:
        raise HTTPException(status_code=404, detail="sig not found")
    if sig.owner != current_user.id:
        raise HTTPException(
            status_code=403, detail="cannot delete sig of other")
    session.delete(sig)
    session.commit()
    return


class BodyUpdateSIG(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content_src: Optional[str] = None
    status: Optional[SIGStatus] = None
    year: Optional[int] = None
    semester: Optional[int] = None


@sig_router.post('/executive/sig/{id}/update', status_code=204)
async def update_sig(id: int, body: BodyUpdateSIG, session: SessionDep) -> None:
    sig = session.get(SIG, id)
    if sig is None:
        raise HTTPException(404, detail="no sig exists")
    if body.title:
        sig.title = body.title
    if body.description:
        sig.description = body.description
    if body.content_src:
        sig.content_src = body.content_src
    if body.status:
        sig.status = body.status
    if body.year:
        if not is_valid_year(body.year):
            raise HTTPException(422, detail="invalid year")
        sig.year = body.year
    if body.semester:
        if not is_valid_semester(body.semester):
            raise HTTPException(422, detail="invalid semester")
        sig.semester = body.semester
    session.add(sig)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail=f"unique field already exists")
    return


@sig_router.post('/executive/sig/{id}/delete', status_code=204)
async def delete_sig(id: int, session: SessionDep) -> None:
    sig = session.get(SIG, id)
    if not sig:
        raise HTTPException(status_code=404, detail="sig not found")
    session.delete(sig)
    session.commit()
    return


@sig_router.get('/sig/{id}/members')
async def get_sig_members(id: int, session: SessionDep) -> Sequence[SIGMember]:
    return session.exec(select(SIGMember).where(SIGMember.ig_id == id)).all()


@sig_router.post('/sig/{id}/member/join', status_code=204)
async def join_sig(id: int, session: SessionDep, current_user: User = Depends(get_current_user)):
    sig = session.get(SIG, id)
    if not sig:
        raise HTTPException(status_code=404, detail="sig not found")
    sig_member = SIGMember(
        ig_id=id,
        user_id=current_user.id
    )
    session.add(sig_member)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail=f"unique field already exists")
    return


@sig_router.post('/sig/{id}/member/leave', status_code=204)
async def leave_sig(id: int, session: SessionDep, current_user: User = Depends(get_current_user)):
    sig = session.get(SIG, id)
    if not sig:
        raise HTTPException(status_code=404, detail="sig not found")
    if sig.owner == current_user.id:
        raise HTTPException(
            status_code=409, detail="sig owner cannot leave the sig")
    sig_member = session.exec(select(SIGMember).where(
        SIGMember.ig_id == id).where(SIGMember.user_id == current_user.id)).first()
    if not sig_member:
        raise HTTPException(status_code=404, detail="sig member not found")
    session.delete(sig_member)
    session.commit()
    return


class BodyExecutiveJoinSIG(BaseModel):
    user_id: str


@sig_router.post('/executive/sig/{id}/member/join', status_code=204)
async def executive_join_sig(id: int, body: BodyExecutiveJoinSIG, session: SessionDep):
    sig = session.get(SIG, id)
    if not sig:
        raise HTTPException(status_code=404, detail="sig not found")
    user = session.get(User, body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    sig_member = SIGMember(
        ig_id=id,
        user_id=body.user_id
    )
    session.add(sig_member)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail=f"unique field already exists")
    return


class BodyExecutiveLeaveSIG(BaseModel):
    user_id: str


@sig_router.post('/executive/sig/{id}/member/leave', status_code=204)
async def executive_leave_sig(id: int, body: BodyExecutiveLeaveSIG, session: SessionDep):
    sig = session.get(SIG, id)
    if not sig:
        raise HTTPException(status_code=404, detail="sig not found")
    user = session.get(User, body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    if sig.owner == user.id:
        raise HTTPException(
            status_code=409, detail="sig owner cannot leave the sig")
    sig_member = session.exec(select(SIGMember).where(
        SIGMember.ig_id == id).where(SIGMember.user_id == body.user_id)).first()
    if not sig_member:
        raise HTTPException(status_code=404, detail="sig member not found")
    session.delete(sig_member)
    session.commit()
    return
