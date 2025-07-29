from typing import Sequence

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.controller import BodyCreatePIG, BodyUpdatePIG, create_pig_ctrl, update_pig_ctrl, ctrl_status_available
from src.db import SessionDep
from src.model import PIG, PIGMember, User
from src.util import SCSCGlobalStatusDep, get_user, get_user_role_level, send_discord_bot_request_no_reply

pig_router = APIRouter(tags=['pig'])


@pig_router.post('/pig/create', status_code=201)
async def create_pig(session: SessionDep, scsc_global_status: SCSCGlobalStatusDep, request: Request, body: BodyCreatePIG) -> PIG:
    current_user = get_user(request)
    return await create_pig_ctrl(session, body, current_user.id, current_user.discord_id, scsc_global_status)


@pig_router.get('/pig/{id}')
async def get_pig_by_id(id: int, session: SessionDep) -> PIG:
    pig = session.get(PIG, id)
    if not pig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
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
    if not pig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    if pig.owner != current_user.id: raise HTTPException(403, detail="타인의 시그/피그를 삭제할 수 없습니다")
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
    if not pig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    session.delete(pig)
    session.commit()
    return


class BodyHandoverPIG(BaseModel):
    new_owner: str


@pig_router.post('/pig/{id}/handover', status_code=204)
async def handover_pig(id: int, session: SessionDep, request: Request, body: BodyHandoverPIG) -> None:
    current_user = get_user(request)
    pig = session.get(PIG, id)
    if pig is None: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    user = session.exec(select(PIGMember).where(PIGMember.ig_id == id).where(
        PIGMember.user_id == body.new_owner)).first()
    if not user: raise HTTPException(status_code=404, detail="새로운 시그/피그장은 해당 시그/피그의 구성원이어야 합니다")
    if current_user.role < get_user_role_level('executive') and current_user.id != pig.owner: raise HTTPException(403, "타인의 시그/피그를 변경할 수 없습니다")
    pig.owner = body.new_owner
    session.add(pig)
    session.commit()
    return


@pig_router.get('/pig/{id}/members')
async def get_pig_members(id: int, session: SessionDep) -> list:
    res = []
    for member in session.exec(select(PIGMember).where(PIGMember.ig_id == id)).all():
        user = session.get(User, member.user_id)
        member_dict = member.model_dump()
        member_dict["user"] = user.model_dump() if user else {}
        res.append(member_dict)
    return res


@pig_router.post('/pig/{id}/member/join', status_code=204)
async def join_pig(id: int, session: SessionDep, request: Request):
    current_user = get_user(request)
    pig = session.get(PIG, id)
    if not pig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    if pig.status not in ctrl_status_available.join_sigpig: raise HTTPException(400, f"SCSC 전역 상태가 {ctrl_status_available.join_sigpig}일 때만 시그/피그에 가입할 수 있습니다")
    pig_member = PIGMember(
        ig_id=id,
        user_id=current_user.id,
        status=pig.status
    )
    session.add(pig_member)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")
    session.refresh(pig)
    if current_user.discord_id: await send_discord_bot_request_no_reply(action_code=2001, body={'user_id': current_user.discord_id, 'role_name': pig.title})
    return


@pig_router.post('/pig/{id}/member/leave', status_code=204)
async def leave_pig(id: int, session: SessionDep, scsc_global_status: SCSCGlobalStatusDep, request: Request):
    current_user = get_user(request)
    pig = session.get(PIG, id)
    if not pig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    if pig.owner == current_user.id: raise HTTPException(409, detail="시그/피그장은 해당 시그/피그를 탈퇴할 수 없습니다")
    pig_member = session.exec(select(PIGMember).where(PIGMember.ig_id == id).where(PIGMember.user_id == current_user.id).where(PIGMember.status == scsc_global_status.status)).first()
    if not pig_member: raise HTTPException(404, detail="시그/피그의 구성원이 아닙니다")
    session.delete(pig_member)
    session.commit()
    session.refresh(pig)
    await send_discord_bot_request_no_reply(action_code=2002, body={'user_id': current_user.discord_id, 'role_name': pig.title})
    return


class BodyExecutiveJoinPIG(BaseModel):
    user_id: str


@pig_router.post('/executive/pig/{id}/member/join', status_code=204)
async def executive_join_pig(id: int, session: SessionDep, body: BodyExecutiveJoinPIG):
    pig = session.get(PIG, id)
    if not pig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    user = session.get(User, body.user_id)
    if not user: raise HTTPException(404, detail="해당 id의 사용자가 없습니다")
    pig_member = PIGMember(
        ig_id=id,
        user_id=body.user_id,
        status=pig.status
    )
    session.add(pig_member)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")
    session.refresh(user)
    session.refresh(pig)
    if user.discord_id: await send_discord_bot_request_no_reply(action_code=2001, body={'user_id': user.discord_id, 'role_name': pig.title})
    return


class BodyExecutiveLeavePIG(BaseModel):
    user_id: str


@pig_router.post('/executive/pig/{id}/member/leave', status_code=204)
async def executive_leave_pig(id: int, session: SessionDep, body: BodyExecutiveLeavePIG):
    pig = session.get(PIG, id)
    if not pig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    user = session.get(User, body.user_id)
    if not user: raise HTTPException(404, detail="해당 id의 사용자가 없습니다")
    if pig.owner == user.id: raise HTTPException(409, detail="시그/피그장은 해당 시그/피그를 탈퇴할 수 없습니다")
    pig_members = session.exec(select(PIGMember).where(PIGMember.ig_id == id).where(PIGMember.user_id == body.user_id)).all()
    if not pig_members: raise HTTPException(404, detail="시그/피그의 구성원이 아닙니다")
    for member in pig_members:
        session.delete(member)
    session.commit()
    session.refresh(user)
    session.refresh(pig)
    await send_discord_bot_request_no_reply(action_code=2002, body={'user_id': user.discord_id, 'role_name': pig.title})
    return
