from typing import Sequence

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.controller import BodyCreateSIG, BodyUpdateSIG, create_sig_ctrl, update_sig_ctrl, ctrl_status_available
from src.db import SessionDep
from src.model import SIG, SIGMember, User
from src.util import SCSCGlobalStatusDep, get_user, get_user_role_level, send_discord_bot_request_no_reply

sig_router = APIRouter(tags=['sig'])


@sig_router.post('/sig/create', status_code=201)
async def create_sig(session: SessionDep, scsc_global_status: SCSCGlobalStatusDep, request: Request, body: BodyCreateSIG) -> SIG:
    current_user = get_user(request)
    return await create_sig_ctrl(session, body, current_user.id, current_user.discord_id, scsc_global_status)


@sig_router.get('/sig/{id}')
async def get_sig_by_id(id: int, session: SessionDep) -> SIG:
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    return sig


@sig_router.get('/sigs')
async def get_all_sigs(session: SessionDep) -> Sequence[SIG]:
    return session.exec(select(SIG)).all()


@sig_router.post('/sig/{id}/update', status_code=204)
async def update_my_sig(id: int, session: SessionDep, request: Request, body: BodyUpdateSIG) -> None:
    current_user = get_user(request)
    await update_sig_ctrl(session, id, body, current_user.id, False)


@sig_router.post('/sig/{id}/delete', status_code=204)
async def delete_my_sig(id: int, session: SessionDep, request: Request) -> None:
    current_user = get_user(request)
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    if sig.owner != current_user.id: raise HTTPException(403, detail="타인의 시그/피그를 삭제할 수 없습니다")
    session.delete(sig)
    session.commit()
    return


@sig_router.post('/executive/sig/{id}/update', status_code=204)
async def update_sig(id: int, session: SessionDep, request: Request, body: BodyUpdateSIG) -> None:
    current_user = get_user(request)
    await update_sig_ctrl(session, id, body, current_user.id, True)


@sig_router.post('/executive/sig/{id}/delete', status_code=204)
async def delete_sig(id: int, session: SessionDep) -> None:
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    session.delete(sig)
    session.commit()
    return


class BodyHandoverSIG(BaseModel):
    new_owner: str


@sig_router.post('/sig/{id}/handover', status_code=204)
async def handover_sig(id: int, session: SessionDep, request: Request, body: BodyHandoverSIG) -> None:
    current_user = get_user(request)
    sig = session.get(SIG, id)
    if sig is None: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    user = session.exec(select(SIGMember).where(SIGMember.ig_id == id).where(
        SIGMember.user_id == body.new_owner)).first()
    if not user: raise HTTPException(status_code=404, detail="새로운 시그/피그장은 해당 시그/피그의 구성원이어야 합니다")
    if current_user.role < get_user_role_level('executive') and current_user.id != sig.owner: raise HTTPException(403, "타인의 시그/피그를 변경할 수 없습니다")
    sig.owner = body.new_owner
    session.add(sig)
    session.commit()
    return


@sig_router.get('/sig/{id}/members')
async def get_sig_members(id: int, session: SessionDep) -> Sequence[SIGMember]:
    return session.exec(select(SIGMember).where(SIGMember.ig_id == id)).all()


@sig_router.post('/sig/{id}/member/join', status_code=204)
async def join_sig(id: int, session: SessionDep, request: Request):
    current_user = get_user(request)
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    if sig.status not in ctrl_status_available.join_sigpig: raise HTTPException(400, f"SCSC 전역 상태가 {ctrl_status_available.join_sigpig}일 때만 시그/피그에 가입할 수 있습니다")
    sig_member = SIGMember(
        ig_id=id,
        user_id=current_user.id,
        status=sig.status
    )
    session.add(sig_member)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")
    session.refresh(sig)
    if current_user.discord_id: await send_discord_bot_request_no_reply(action_code=2001, body={'user_id': current_user.discord_id, 'role_name': sig.title})
    return


@sig_router.post('/sig/{id}/member/leave', status_code=204)
async def leave_sig(id: int, session: SessionDep, scsc_global_status: SCSCGlobalStatusDep, request: Request):
    current_user = get_user(request)
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    if sig.owner == current_user.id: raise HTTPException(409, detail="시그/피그장은 해당 시그/피그를 탈퇴할 수 없습니다")
    sig_member = session.exec(select(SIGMember).where(SIGMember.ig_id == id).where(SIGMember.user_id == current_user.id).where(SIGMember.status == scsc_global_status.status)).first()
    if not sig_member: raise HTTPException(404, detail="시그/피그의 구성원이 아닙니다")
    session.delete(sig_member)
    session.commit()
    session.refresh(sig)
    await send_discord_bot_request_no_reply(action_code=2002, body={'user_id': current_user.discord_id, 'role_name': sig.title})
    return


class BodyExecutiveJoinSIG(BaseModel):
    user_id: str


@sig_router.post('/executive/sig/{id}/member/join', status_code=204)
async def executive_join_sig(id: int, session: SessionDep, body: BodyExecutiveJoinSIG):
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    user = session.get(User, body.user_id)
    if not user: raise HTTPException(404, detail="해당 id의 사용자가 없습니다")
    sig_member = SIGMember(
        ig_id=id,
        user_id=body.user_id,
        status=sig.status
    )
    session.add(sig_member)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")
    session.refresh(user)
    session.refresh(sig)
    if user.discord_id: await send_discord_bot_request_no_reply(action_code=2001, body={'user_id': user.discord_id, 'role_name': sig.title})
    return


class BodyExecutiveLeaveSIG(BaseModel):
    user_id: str


@sig_router.post('/executive/sig/{id}/member/leave', status_code=204)
async def executive_leave_sig(id: int, session: SessionDep, body: BodyExecutiveLeaveSIG):
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    user = session.get(User, body.user_id)
    if not user: raise HTTPException(404, detail="해당 id의 사용자가 없습니다")
    if sig.owner == user.id: raise HTTPException(409, detail="시그/피그장은 해당 시그/피그를 탈퇴할 수 없습니다")
    sig_members = session.exec(select(SIGMember).where(SIGMember.ig_id == id).where(SIGMember.user_id == body.user_id)).all()
    if not sig_members: raise HTTPException(404, detail="시그/피그의 구성원이 아닙니다")
    for member in sig_members:
        session.delete(member)
    session.commit()
    session.refresh(user)
    session.refresh(sig)
    await send_discord_bot_request_no_reply(action_code=2002, body={'user_id': user.discord_id, 'role_name': sig.title})
    return
