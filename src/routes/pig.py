from typing import Sequence

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.controller import BodyCreatePIG, BodyUpdatePIG, create_pig_ctrl, update_pig_ctrl
from src.db import SessionDep
from src.model import PIG, PIGMember, SCSCStatus, User
from src.util import SCSCGlobalStatusDep, get_user, get_user_role_level

pig_router = APIRouter(tags=['pig'])


@pig_router.post('/pig/create', status_code=201)
async def create_pig(session: SessionDep, scsc_global_status: SCSCGlobalStatusDep, request: Request, body: BodyCreatePIG) -> PIG:
    current_user = get_user(request)
    return await create_pig_ctrl(session, body, current_user.id, scsc_global_status)


@pig_router.get('/pig/{id}')
async def get_pig_by_id(id: int, session: SessionDep) -> PIG:
    pig = session.get(PIG, id)
    if not pig: raise HTTPException(404, detail="pig not found")
    return pig


@pig_router.get('/pigs')
async def get_all_pigs(session: SessionDep) -> Sequence[PIG]:
    return session.exec(select(PIG)).all()


@pig_router.post('/pig/{id}/update', status_code=204)
async def update_my_pig(id: int, session: SessionDep, request: Request, body: BodyUpdatePIG) -> None:
    current_user = get_user(request)
    await update_pig_ctrl(session, id, body, current_user.id, False)


@pig_router.post('/pig/{id}/delete', status_code=204)
async def delete_my_pig(id: int, session: SessionDep, request: Request) -> None:
    current_user = get_user(request)
    pig = session.get(PIG, id)
    if not pig: raise HTTPException(404, detail="pig not found")
    if pig.owner != current_user.id: raise HTTPException(403, detail="cannot delete pig of other")
    session.delete(pig)
    session.commit()
    return


@pig_router.post('/executive/pig/{id}/update', status_code=204)
async def update_pig(id: int, session: SessionDep, request: Request, body: BodyUpdatePIG) -> None:
    current_user = get_user(request)
    await update_pig_ctrl(session, id, body, current_user.id, True)


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
async def handover_pig(id: int, session: SessionDep, request: Request, body: BodyHandoverPIG) -> None:
    current_user = get_user(request)
    pig = session.get(PIG, id)
    if pig is None: raise HTTPException(404, detail="no pig exists")
    user = session.exec(select(PIGMember).where(PIGMember.ig_id == id).where(
        PIGMember.user_id == body.new_owner)).first()
    if not user: raise HTTPException(
        status_code=404, detail="new_owner should be a member of the pig")
    if current_user.role < get_user_role_level('executive') and current_user.id != pig.owner: raise HTTPException(403, "handover can be executed only by executive or owner of the pig")
    pig.owner = body.new_owner
    session.add(pig)
    session.commit()
    return


@pig_router.get('/pig/{id}/members')
async def get_pig_members(id: int, session: SessionDep) -> Sequence[PIGMember]:
    return session.exec(select(PIGMember).where(PIGMember.ig_id == id)).all()


@pig_router.post('/pig/{id}/member/join', status_code=204)
async def join_pig(id: int, session: SessionDep, request: Request):
    current_user = get_user(request)
    pig = session.get(PIG, id)
    if not pig: raise HTTPException(404, detail="pig not found")
    if pig.status not in (SCSCStatus.surveying, SCSCStatus.recruiting): raise HTTPException(400, "cannot join to pig when pig status is not surveying/recruiting")
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
async def leave_pig(id: int, session: SessionDep, scsc_global_status: SCSCGlobalStatusDep, request: Request):
    current_user = get_user(request)
    pig = session.get(PIG, id)
    if not pig: raise HTTPException(404, detail="pig not found")
    if pig.owner == current_user.id: raise HTTPException(409, detail="pig owner cannot leave the pig")
    pig_member = session.exec(select(PIGMember).where(PIGMember.ig_id == id).where(PIGMember.user_id == current_user.id).where(PIGMember.status == scsc_global_status.status)).first()
    if not pig_member: raise HTTPException(404, detail="pig member not found")
    session.delete(pig_member)
    session.commit()
    return


class BodyExecutiveJoinPIG(BaseModel):
    user_id: str


@pig_router.post('/executive/pig/{id}/member/join', status_code=204)
async def executive_join_pig(id: int, session: SessionDep, body: BodyExecutiveJoinPIG):
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
async def executive_leave_pig(id: int, session: SessionDep, body: BodyExecutiveLeavePIG):
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
