from typing import Sequence

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.controller import BodyCreateSIG, BodyUpdateSIG, create_sig_ctrl, update_sig_ctrl, ctrl_status_available
from src.db import SessionDep
from src.model import SIG, SIGMember, User, SCSCStatus, SCSCGlobalStatus
from src.util import SCSCGlobalStatusDep, get_user, get_user_role_level, send_discord_bot_request_no_reply
from src.controller.scsc import _map_semester_name

sig_router = APIRouter(tags=['sig'])


@sig_router.post('/sig/create', status_code=201)
async def create_sig(session: SessionDep, scsc_global_status: SCSCGlobalStatusDep, request: Request, body: BodyCreateSIG) -> SIG:
    current_user = get_user(request)
    if not current_user.discord_id: raise HTTPException(409, 'No discord ID found, creator must enroll in the discord server first')
    return await create_sig_ctrl(session, body, current_user.id, current_user.discord_id, scsc_global_status)


@sig_router.get('/sig/{id}')
async def get_sig_by_id(id: int, session: SessionDep) -> SIG:
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="sig not found")
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
    if not sig: raise HTTPException(404, detail="sig not found")
    if sig.owner != current_user.id: raise HTTPException(403, detail="cannot delete sig of other")
    sig.status = SCSCStatus.inactive
    session.commit()
    year = sig.year
    semester = sig.semester
    await send_discord_bot_request_no_reply(action_code=4002, body={'sig_name': sig.title,
                                                                    "previous_semester": f"{year}-{_map_semester_name.get(semester)}"})
    return


@sig_router.post('/executive/sig/{id}/update', status_code=204)
async def update_sig(id: int, session: SessionDep, request: Request, body: BodyUpdateSIG) -> None:
    current_user = get_user(request)
    await update_sig_ctrl(session, id, body, current_user.id, True)


@sig_router.post('/executive/sig/{id}/delete', status_code=204)
async def delete_sig(id: int, session: SessionDep) -> None:
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="sig not found")
    sig.status = SCSCStatus.inactive
    session.commit()
    year = sig.year
    semester = sig.semester
    await send_discord_bot_request_no_reply(action_code=4002, body={'sig_name': sig.title,
                                                                    "previous_semester": f"{year}-{_map_semester_name.get(semester)}"})
    return


class BodyHandoverSIG(BaseModel):
    new_owner: str


@sig_router.post('/sig/{id}/handover', status_code=204)
async def handover_sig(id: int, session: SessionDep, request: Request, body: BodyHandoverSIG) -> None:
    current_user = get_user(request)
    sig = session.get(SIG, id)
    if sig is None: raise HTTPException(404, detail="no sig exists")
    user = session.exec(select(SIGMember).where(SIGMember.ig_id == id).where(
        SIGMember.user_id == body.new_owner)).first()
    if not user: raise HTTPException(
        status_code=404, detail="new_owner should be a member of the sig")
    if current_user.role < get_user_role_level('executive') and current_user.id != sig.owner: raise HTTPException(403, "handover can be executed only by executive or owner of the sig")
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
    if not sig: raise HTTPException(404, detail="sig not found")
    if sig.status not in ctrl_status_available.join_sigpig: raise HTTPException(400, f"cannot join to sig when sig status is not in {ctrl_status_available.join_sigpig}")
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
    session.refresh(sig)
    if not current_user.discord_id: raise HTTPException(409, 'No discord ID found, user must enroll in the discord server first')
    await send_discord_bot_request_no_reply(action_code=2001, body={'user_id': current_user.discord_id, 'role_name': sig.title})
    return


@sig_router.post('/sig/{id}/member/leave', status_code=204)
async def leave_sig(id: int, session: SessionDep, scsc_global_status: SCSCGlobalStatusDep, request: Request):
    current_user = get_user(request)
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="sig not found")
    if sig.owner == current_user.id: raise HTTPException(409, detail="sig owner cannot leave the sig")
    sig_member = session.exec(select(SIGMember).where(SIGMember.ig_id == id).where(SIGMember.user_id == current_user.id).where(SIGMember.status == scsc_global_status.status)).first()
    if not sig_member: raise HTTPException(404, detail="sig member not found")
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
    session.refresh(user)
    session.refresh(sig)
    if not user.discord_id: raise HTTPException(409, 'No discord ID found, creator must enroll in the discord server first')
    await send_discord_bot_request_no_reply(action_code=2001, body={'user_id': user.discord_id, 'role_name': sig.title})
    return


class BodyExecutiveLeaveSIG(BaseModel):
    user_id: str


@sig_router.post('/executive/sig/{id}/member/leave', status_code=204)
async def executive_leave_sig(id: int, session: SessionDep, body: BodyExecutiveLeaveSIG):
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
    session.refresh(user)
    session.refresh(sig)
    await send_discord_bot_request_no_reply(action_code=2002, body={'user_id': user.discord_id, 'role_name': sig.title})
    return
