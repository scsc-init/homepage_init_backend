from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.auth import get_current_user
from src.db import SessionDep
from src.model import PIG, PIGGlobalStatus, PIGMember, PIGStatus, User, UserRole
from src.util import get_pig_global_status
from src.controller import create_pig_controller, BodyCreatePIG, update_pig_controller, BodyUpdatePIG


pig_router = APIRouter(tags=['pig'])


@pig_router.post('/pig/create', status_code=201)
async def create_pig(body: BodyCreatePIG, session: SessionDep, current_user: User = Depends(get_current_user), pig_global_status: PIGGlobalStatus = Depends(get_pig_global_status)) -> PIG:
    return await create_pig_controller(session, body, current_user.id, pig_global_status)


@pig_router.get('/pig/{id}')
async def get_pig_by_id(id: int, session: SessionDep) -> PIG:
    pig = session.get(PIG, id)
    if not pig: raise HTTPException(404, detail="pig not found")
    return pig


@pig_router.get('/pigs')
async def get_all_pigs(session: SessionDep) -> Sequence[PIG]:
    return session.exec(select(PIG)).all()


@pig_router.post('/pig/{id}/update', status_code=204)
async def update_my_pig(id: int, body: BodyUpdatePIG, session: SessionDep, current_user: User = Depends(get_current_user)) -> None:
    await update_pig_controller(session, id, body, current_user.id, False)


@pig_router.post('/pig/{id}/delete', status_code=204)
async def delete_my_pig(id: int, session: SessionDep, current_user: User = Depends(get_current_user)) -> None:
    pig = session.get(PIG, id)
    if not pig: raise HTTPException(404, detail="pig not found")
    if pig.owner != current_user.id: raise HTTPException(403, detail="cannot delete pig of other")
    session.delete(pig)
    session.commit()
    return


@pig_router.post('/executive/pig/{id}/update', status_code=204)
async def update_pig(id: int, body: BodyUpdatePIG, session: SessionDep, current_user: User = Depends(get_current_user)) -> None:
    await update_pig_controller(session, id, body, current_user.id, True)


@pig_router.post('/executive/pig/{id}/delete', status_code=204)
async def delete_pig(id: int, session: SessionDep) -> None:
    pig = session.get(PIG, id)
    if not pig: raise HTTPException(404, detail="pig not found")
    session.delete(pig)
    session.commit()
    return


class BodyHandoverPIG(BaseModel):
    new_owner: str


@pig_router.post('/pig/{id}/handover', status_code=204)
async def handover_pig(id: int, body: BodyHandoverPIG, session: SessionDep, current_user: User = Depends(get_current_user)) -> None:
    pig = session.get(PIG, id)
    if pig is None: raise HTTPException(404, detail="no pig exists")
    user = session.exec(select(PIGMember).where(PIGMember.ig_id == id).where(
        PIGMember.user_id == body.new_owner)).first()
    if not user: raise HTTPException(
        status_code=404, detail="new_owner should be a member of the pig")
    if current_user.role < UserRole.executive and current_user.id != pig.owner: raise HTTPException(403, "handover can be executed only by executive or owner of the pig")
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
    if not pig: raise HTTPException(404, detail="pig not found")
    if pig.status not in (PIGStatus.surveying, PIGStatus.recruiting): raise HTTPException(400, "cannot join to pig when pig status is not surveying/recruiting")
    pig_member = PIGMember(
        ig_id=id,
        user_id=current_user.id,
        status=pig.status
    )
    session.add(pig_member)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="unique field already exists")
    return


@pig_router.post('/pig/{id}/member/leave', status_code=204)
async def leave_pig(id: int, session: SessionDep, current_user: User = Depends(get_current_user), pig_global_status: PIGGlobalStatus = Depends(get_pig_global_status)):
    pig = session.get(PIG, id)
    if not pig: raise HTTPException(404, detail="pig not found")
    if pig.owner == current_user.id: raise HTTPException(409, detail="pig owner cannot leave the pig")
    pig_member = session.exec(select(PIGMember).where(PIGMember.ig_id == id).where(PIGMember.user_id == current_user.id).where(PIGMember.status == pig_global_status.status)).first()
    if not pig_member: raise HTTPException(404, detail="pig member not found")
    session.delete(pig_member)
    session.commit()
    return


class BodyExecutiveJoinPIG(BaseModel):
    user_id: str


@pig_router.post('/executive/pig/{id}/member/join', status_code=204)
async def executive_join_pig(id: int, body: BodyExecutiveJoinPIG, session: SessionDep):
    pig = session.get(PIG, id)
    if not pig: raise HTTPException(404, detail="pig not found")
    user = session.get(User, body.user_id)
    if not user: raise HTTPException(404, detail="user not found")
    pig_member = PIGMember(
        ig_id=id,
        user_id=body.user_id,
        status=pig.status
    )
    session.add(pig_member)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="unique field already exists")
    return


class BodyExecutiveLeavePIG(BaseModel):
    user_id: str


@pig_router.post('/executive/pig/{id}/member/leave', status_code=204)
async def executive_leave_pig(id: int, body: BodyExecutiveLeavePIG, session: SessionDep):
    pig = session.get(PIG, id)
    if not pig: raise HTTPException(404, detail="pig not found")
    user = session.get(User, body.user_id)
    if not user: raise HTTPException(404, detail="user not found")
    if pig.owner == user.id: raise HTTPException(409, detail="pig owner cannot leave the pig")
    pig_members = session.exec(select(PIGMember).where(PIGMember.ig_id == id).where(PIGMember.user_id == body.user_id)).all()
    if not pig_members: raise HTTPException(404, detail="pig member not found")
    for member in pig_members:
        session.delete(member)
    session.commit()
    return


@pig_router.get('/pig/global/status')
async def _get_pig_global_status(pig_global_status: PIGGlobalStatus = Depends(get_pig_global_status)):
    return {'status': pig_global_status.status}


class BodyUpdatePIGGlobalStatus(BaseModel):
    status: PIGStatus


_valid_pig_global_status_update = (
    (PIGStatus.inactive, PIGStatus.surveying),
    (PIGStatus.surveying, PIGStatus.recruiting),
    (PIGStatus.recruiting, PIGStatus.active),
    (PIGStatus.surveying, PIGStatus.inactive),
    (PIGStatus.recruiting, PIGStatus.inactive),
    (PIGStatus.active, PIGStatus.inactive),
)


def _check_valid_pig_global_status_update(old_status: PIGStatus, new_status: PIGStatus) -> bool:
    for valid_update in _valid_pig_global_status_update:
        if (old_status, new_status) == valid_update: return True
    return False


@pig_router.post('/executive/pig/global/status', status_code=204)
async def update_pig_global_status(body: BodyUpdatePIGGlobalStatus, session: SessionDep, pig_global_status: PIGGlobalStatus = Depends(get_pig_global_status)):
    if not _check_valid_pig_global_status_update(pig_global_status.status, body.status): raise HTTPException(400, "invalid pig global status update")
    if body.status == PIGStatus.inactive:
        pigs = session.exec(select(PIG).where(PIG.status != PIGStatus.inactive)).all()
        for pig in pigs:
            pig.status = PIGStatus.inactive
            session.add(pig)
    elif body.status in (PIGStatus.recruiting, PIGStatus.active):
        pigs = session.exec(select(PIG).where(PIG.status == pig_global_status.status)).all()
        for pig in pigs:
            pig.status = body.status
            session.add(pig)
    pig_global_status.status = body.status
    session.add(pig_global_status)
    session.commit()
    return
