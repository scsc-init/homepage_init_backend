from typing import Optional, Sequence

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.auth import get_current_user
from src.db import SessionDep
from src.model import SIG, SIGGlobalStatus, SIGMember, SIGStatus, User, UserRole
from src.util import is_valid_semester, is_valid_year
from src.util import get_sig_global_status

sig_router = APIRouter(tags=['sig'])


class BodyCreateSIG(BaseModel):
    title: str
    description: str
    content_src: str
    year: int
    semester: int


@sig_router.post('/sig/create', status_code=201)
async def create_sig(body: BodyCreateSIG, session: SessionDep, current_user: User = Depends(get_current_user), sig_global_status: SIGGlobalStatus = Depends(get_sig_global_status)) -> SIG:
    if sig_global_status.status != SIGStatus.surveying: raise HTTPException(400, "cannot create sig when sig global status is not surveying")
    if not is_valid_year(body.year): raise HTTPException(422, detail="invalid year")
    if not is_valid_semester(body.semester): raise HTTPException(422, detail="invalid semester")

    sig = SIG(
        title=body.title,
        description=body.description,
        content_src=body.content_src,
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


@sig_router.get('/sig/{id}')
async def get_sig_by_id(id: int, session: SessionDep) -> SIG:
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="sig not found")
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
    if not sig: raise HTTPException(404, detail="sig not found")
    if sig.owner != current_user.id: raise HTTPException(
        status_code=403, detail="cannot update sig of other")
    if not is_valid_year(body.year): raise HTTPException(422, detail="invalid year")
    if not is_valid_semester(body.semester): raise HTTPException(422, detail="invalid semester")

    sig.title = body.title
    sig.description = body.description
    sig.content_src = body.content_src
    sig.year = body.year
    sig.semester = body.semester
    session.add(sig)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="unique field already exists")
    return


@sig_router.post('/sig/{id}/delete', status_code=204)
async def delete_my_sig(id: int, session: SessionDep, current_user: User = Depends(get_current_user)) -> None:
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="sig not found")
    if sig.owner != current_user.id: raise HTTPException(403, detail="cannot delete sig of other")
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
    if sig is None: raise HTTPException(404, detail="no sig exists")
    if body.title:
        sig.title = body.title
    if body.description:
        sig.description = body.description
    if body.content_src:
        sig.content_src = body.content_src
    if body.status:
        sig.status = body.status
    if body.year:
        if not is_valid_year(body.year): raise HTTPException(422, detail="invalid year")
        sig.year = body.year
    if body.semester:
        if not is_valid_semester(body.semester): raise HTTPException(422, detail="invalid semester")
        sig.semester = body.semester
    session.add(sig)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="unique field already exists")
    return


@sig_router.post('/executive/sig/{id}/delete', status_code=204)
async def delete_sig(id: int, session: SessionDep) -> None:
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="sig not found")
    session.delete(sig)
    session.commit()
    return


class BodyHandoverSIG(BaseModel):
    new_owner: str


@sig_router.post('/sig/{id}/handover', status_code=204)
async def handover_sig(id: int, body: BodyHandoverSIG, session: SessionDep, current_user: User = Depends(get_current_user)) -> None:
    sig = session.get(SIG, id)
    if sig is None: raise HTTPException(404, detail="no sig exists")
    user = session.exec(select(SIGMember).where(SIGMember.ig_id == id).where(
        SIGMember.user_id == body.new_owner)).first()
    if not user: raise HTTPException(
        status_code=404, detail="new_owner should be a member of the sig")
    if current_user.role < UserRole.executive and current_user.id != sig.owner: raise HTTPException(403, "handover can be executed only by executive or owner of the sig")
    sig.owner = body.new_owner
    session.add(sig)
    session.commit()
    return


@sig_router.get('/sig/{id}/members')
async def get_sig_members(id: int, session: SessionDep) -> Sequence[SIGMember]:
    return session.exec(select(SIGMember).where(SIGMember.ig_id == id)).all()


@sig_router.post('/sig/{id}/member/join', status_code=204)
async def join_sig(id: int, session: SessionDep, current_user: User = Depends(get_current_user)):
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="sig not found")
    if sig.status not in (SIGStatus.surveying, SIGStatus.recruiting): raise HTTPException(400, "cannot join to sig when sig status is not surveying/recruiting")
    sig_member = SIGMember(
        ig_id=id,
        user_id=current_user.id,
        status=sig.status
    )
    session.add(sig_member)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="unique field already exists")
    return


@sig_router.post('/sig/{id}/member/leave', status_code=204)
async def leave_sig(id: int, session: SessionDep, current_user: User = Depends(get_current_user), sig_global_status: SIGGlobalStatus = Depends(get_sig_global_status)):
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="sig not found")
    if sig.owner == current_user.id: raise HTTPException(409, detail="sig owner cannot leave the sig")
    sig_member = session.exec(select(SIGMember).where(SIGMember.ig_id == id).where(SIGMember.user_id == current_user.id).where(SIGMember.status == sig_global_status.status)).first()
    if not sig_member: raise HTTPException(404, detail="sig member not found")
    session.delete(sig_member)
    session.commit()
    return


class BodyExecutiveJoinSIG(BaseModel):
    user_id: str


@sig_router.post('/executive/sig/{id}/member/join', status_code=204)
async def executive_join_sig(id: int, body: BodyExecutiveJoinSIG, session: SessionDep):
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="sig not found")
    user = session.get(User, body.user_id)
    if not user: raise HTTPException(404, detail="user not found")
    sig_member = SIGMember(
        ig_id=id,
        user_id=body.user_id,
        status=sig.status
    )
    session.add(sig_member)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="unique field already exists")
    return


class BodyExecutiveLeaveSIG(BaseModel):
    user_id: str


@sig_router.post('/executive/sig/{id}/member/leave', status_code=204)
async def executive_leave_sig(id: int, body: BodyExecutiveLeaveSIG, session: SessionDep):
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="sig not found")
    user = session.get(User, body.user_id)
    if not user: raise HTTPException(404, detail="user not found")
    if sig.owner == user.id: raise HTTPException(409, detail="sig owner cannot leave the sig")
    sig_members = session.exec(select(SIGMember).where(SIGMember.ig_id == id).where(SIGMember.user_id == body.user_id)).all()
    if not sig_members: raise HTTPException(404, detail="sig member not found")
    for member in sig_members:
        session.delete(member)
    session.commit()
    return


@sig_router.get('/sig/global/status')
async def _get_sig_global_status(sig_global_status: SIGGlobalStatus = Depends(get_sig_global_status)):
    return {'status': sig_global_status.status}


class BodyUpdateSIGGlobalStatus(BaseModel):
    status: SIGStatus


_valid_sig_global_status_update = (
    (SIGStatus.inactive, SIGStatus.surveying),
    (SIGStatus.surveying, SIGStatus.recruiting),
    (SIGStatus.recruiting, SIGStatus.active),
    (SIGStatus.surveying, SIGStatus.inactive),
    (SIGStatus.recruiting, SIGStatus.inactive),
    (SIGStatus.active, SIGStatus.inactive),
)


def _check_valid_sig_global_status_update(old_status: SIGStatus, new_status: SIGStatus) -> bool:
    for valid_update in _valid_sig_global_status_update:
        if (old_status, new_status) == valid_update: return True
    return False


@sig_router.post('/executive/sig/global/status', status_code=204)
async def update_sig_global_status(body: BodyUpdateSIGGlobalStatus, session: SessionDep, sig_global_status: SIGGlobalStatus = Depends(get_sig_global_status)):
    if not _check_valid_sig_global_status_update(sig_global_status.status, body.status): raise HTTPException(400, "invalid sig global status update")
    if body.status == SIGStatus.inactive:
        sigs = session.exec(select(SIG).where(SIG.status != SIGStatus.inactive)).all()
        for sig in sigs:
            sig.status = SIGStatus.inactive
            session.add(sig)
    elif body.status in (SIGStatus.recruiting, SIGStatus.active):
        sigs = session.exec(select(SIG).where(SIG.status == sig_global_status.status)).all()
        for sig in sigs:
            sig.status = body.status
            session.add(sig)
    sig_global_status.status = body.status
    session.add(sig_global_status)
    session.commit()
    return
