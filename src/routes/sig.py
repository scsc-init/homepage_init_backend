from typing import Sequence
import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.controller import BodyCreateSIG, BodyUpdateSIG, create_sig_ctrl, update_sig_ctrl, ctrl_status_available, map_semester_name
from src.db import SessionDep
from src.model import SIG, SIGMember, User, SCSCStatus
from src.util import SCSCGlobalStatusDep, get_user, get_user_role_level, send_discord_bot_request_no_reply

logger = logging.getLogger("app")

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
    if sig.status == SCSCStatus.inactive: raise HTTPException(400, detail="해당 시그/피그는 이미 비활성 상태입니다")
    sig.status = SCSCStatus.inactive
    session.commit()
    session.refresh(sig)
    year = sig.year
    semester = sig.semester
    await send_discord_bot_request_no_reply(action_code=4002, body={'sig_name': sig.title, "previous_semester": f"{year}-{map_semester_name.get(semester)}"})
    logger.info(f'info_type=sig_deleted ; sig_id={sig.id} ; title={sig.title} ; remover_id={current_user.id} ; year={sig.year} ; semester={sig.semester}')
    return


@sig_router.post('/executive/sig/{id}/update', status_code=204)
async def update_sig(id: int, session: SessionDep, request: Request, body: BodyUpdateSIG) -> None:
    current_user = get_user(request)
    await update_sig_ctrl(session, id, body, current_user.id, True)


@sig_router.post('/executive/sig/{id}/delete', status_code=204)
async def delete_sig(id: int, session: SessionDep, request: Request) -> None:
    current_user = get_user(request)
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    if sig.status == SCSCStatus.inactive: raise HTTPException(400, detail="해당 시그/피그는 이미 비활성 상태입니다")
    sig.status = SCSCStatus.inactive
    session.commit()
    session.refresh(sig)
    year = sig.year
    semester = sig.semester
    await send_discord_bot_request_no_reply(action_code=4002, body={'sig_name': sig.title, "previous_semester": f"{year}-{map_semester_name.get(semester)}"})
    logger.info(f'info_type=sig_deleted ; sig_id={sig.id} ; title={sig.title} ; remover_id={current_user.id} ; year={sig.year} ; semester={sig.semester}')
    return


class BodyHandoverSIG(BaseModel):
    new_owner: str


def _handover_sig(session: SessionDep, sig: SIG, new_owner_id: str) -> tuple[SIG, str]:
    """
    Assigns a new owner to a SIG after verifying the specified user is a member.
    
    Parameters:
        sig (SIG): The SIG to update.
        new_owner_id (str): User ID of the member to become the new owner.
    
    Returns:
        tuple[SIG, str]: A tuple containing the updated SIG and the previous owner's user ID.
    
    Raises:
        HTTPException: 404 if the specified new_owner_id is not a member of the SIG.
    """
    member = session.exec(select(SIGMember).where(SIGMember.ig_id == sig.id).where(
        SIGMember.user_id == new_owner_id)).first()
    if not member:
        raise HTTPException(status_code=404, detail="새로운 시그/피그장은 해당 시그/피그의 구성원이어야 합니다")
    old_owner = sig.owner
    sig.owner = new_owner_id
    session.add(sig)
    return sig, old_owner


@sig_router.post('/sig/{id}/handover', status_code=204)
async def handover_sig(id: int, session: SessionDep, request: Request, body: BodyHandoverSIG) -> None:
    """
    Transfer ownership of the specified SIG to another member, performing authorization checks and persisting the change.
    
    Parameters:
        id (int): Primary key of the SIG to transfer.
        body (BodyHandoverSIG): Request body containing `new_owner` — the user ID of the member to become the new owner.
    
    Raises:
        HTTPException: 404 if the SIG does not exist or the specified new owner is not a member.
        HTTPException: 403 if the caller is neither the current owner nor has executive privileges.
    
    Notes:
        The function updates the SIG's owner, logs the handover (including whether it was forced or voluntary), and commits the change to the database.
    """
    current_user = get_user(request)
    sig = session.get(SIG, id)
    if sig is None:
        raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    if current_user.role < get_user_role_level('executive') and current_user.id != sig.owner:
        raise HTTPException(403, "타인의 시그/피그를 변경할 수 없습니다")
    sig, old_owner = _handover_sig(session, sig, body.new_owner)
    handover_type = 'forced' if current_user.id != old_owner else 'voluntary'
    logger.info(
        f'info_type=sig_handover ; handover_type={handover_type} ; sig_id={sig.id} ; title={sig.title} ; '
        f'executor_id={current_user.id} ; old_owner_id={old_owner} ; new_owner_id={body.new_owner} ; '
        f'year={sig.year} ; semester={sig.semester}'
    )
    session.commit()
    return


@sig_router.post('/executive/sig/{id}/handover', status_code=204)
async def executive_handover_sig(id: int, session: SessionDep, request: Request, body: BodyHandoverSIG) -> None:
    """
    Forcefully transfer ownership of a SIG to another member, performed by an executive.
    
    Parameters:
        id (int): Primary key of the SIG to modify.
        body (BodyHandoverSIG): Payload containing `new_owner`, the user id of the member to become the new owner.
    
    Raises:
        HTTPException(403): If the requester is not an executive.
        HTTPException(404): If the SIG does not exist or the specified new owner is not a member of the SIG.
    """
    current_user = get_user(request)
    if current_user.role < get_user_role_level('executive'):
        raise HTTPException(403, detail="임원진만 시그/피그장을 양도할 수 있습니다")
    sig = session.get(SIG, id)
    if sig is None:
        raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    sig, old_owner = _handover_sig(session, sig, body.new_owner)
    logger.info(
        f'info_type=sig_handover ; handover_type=forced ; sig_id={sig.id} ; title={sig.title} ; '
        f'executor_id={current_user.id} ; old_owner_id={old_owner} ; new_owner_id={body.new_owner} ; '
        f'year={sig.year} ; semester={sig.semester}'
    )
    session.commit()
    return


@sig_router.get('/sig/{id}/members')
async def get_sig_members(id: int, session: SessionDep) -> list:
    res = []
    for member in session.exec(select(SIGMember).where(SIGMember.ig_id == id)).all():
        user = session.get(User, member.user_id)
        member_dict = member.model_dump()
        member_dict["user"] = user.model_dump() if user else {}
        res.append(member_dict)
    return res


@sig_router.post('/sig/{id}/member/join', status_code=204)
async def join_sig(id: int, session: SessionDep, request: Request):
    current_user = get_user(request)
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    allowed = (ctrl_status_available.join_sigpig_rolling_admission if sig.is_rolling_admission else ctrl_status_available.join_sigpig)
    if sig.status not in allowed: raise HTTPException(400, f"시그/피그 상태가 {allowed}일 때만 시그/피그에 가입할 수 있습니다")

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
    logger.info(f'info_type=sig_join ; sig_id={sig.id} ; title={sig.title} ; executor_id={current_user.id} ; joined_user_id={current_user.id} ; year={sig.year} ; semester={sig.semester}')
    return


@sig_router.post('/sig/{id}/member/leave', status_code=204)
async def leave_sig(id: int, session: SessionDep, request: Request):
    current_user = get_user(request)
    sig = session.get(SIG, id)
    if not sig: raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    allowed = (ctrl_status_available.join_sigpig_rolling_admission if sig.is_rolling_admission else ctrl_status_available.join_sigpig)
    if sig.status not in allowed: raise HTTPException(400, f"시그/피그 상태가 {allowed}일 때만 시그/피그에서 탈퇴할 수 있습니다")
    if sig.owner == current_user.id: raise HTTPException(409, detail="시그/피그장은 해당 시그/피그를 탈퇴할 수 없습니다")
    sig_members = session.exec(select(SIGMember).where(SIGMember.ig_id == id).where(SIGMember.user_id == current_user.id)).all()
    if not sig_members: raise HTTPException(404, detail="시그/피그의 구성원이 아닙니다")
    for member in sig_members:
        session.delete(member)
    session.commit()
    session.refresh(sig)
    if current_user.discord_id: await send_discord_bot_request_no_reply(action_code=2002, body={'user_id': current_user.discord_id, 'role_name': sig.title})
    logger.info(f'info_type=sig_leave ; sig_id={sig.id} ; title={sig.title} ; executor_id={current_user.id} ; left_user_id={current_user.id} ; year={sig.year} ; semester={sig.semester}')
    return


class BodyExecutiveJoinSIG(BaseModel):
    user_id: str


@sig_router.post('/executive/sig/{id}/member/join', status_code=204)
async def executive_join_sig(id: int, session: SessionDep, request: Request, body: BodyExecutiveJoinSIG):
    current_user = get_user(request)
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
    logger.info(f'info_type=sig_join ; sig_id={sig.id} ; title={sig.title} ; executor_id={current_user.id} ; joined_user_id={body.user_id} ; year={sig.year} ; semester={sig.semester}')
    return


class BodyExecutiveLeaveSIG(BaseModel):
    user_id: str


@sig_router.post('/executive/sig/{id}/member/leave', status_code=204)
async def executive_leave_sig(id: int, session: SessionDep, request: Request, body: BodyExecutiveLeaveSIG):
    current_user = get_user(request)
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
    logger.info(f'info_type=sig_leave ; sig_id={sig.id} ; title={sig.title} ; executor_id={current_user.id} ; left_user_id={body.user_id} ; year={sig.year} ; semester={sig.semester}')
    return