from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import logging

from fastapi import HTTPException, Request
from sqlmodel import select

from src.db import SessionDep
from src.model import PIG, SIG, OldboyApplicant, SCSCGlobalStatus, SCSCStatus, User, UserStatus, StandbyReqTbl
from src.util import map_semester_name, get_user_role_level, change_discord_role, send_discord_bot_request_no_reply, send_discord_bot_request, get_new_year_semester, process_igs

from .user import process_oldboy_applicant_ctrl

logger = logging.getLogger("app")

_valid_scsc_global_status_update = (
    (SCSCStatus.inactive, SCSCStatus.surveying),
    (SCSCStatus.surveying, SCSCStatus.recruiting),
    (SCSCStatus.recruiting, SCSCStatus.active),
    (SCSCStatus.active, SCSCStatus.surveying),
    (SCSCStatus.active, SCSCStatus.inactive),
)


@dataclass
class _CtrlStatusAvailable:
    create_sigpig: tuple[SCSCStatus, SCSCStatus]
    join_sigpig: tuple[SCSCStatus, SCSCStatus]


ctrl_status_available = _CtrlStatusAvailable(
    create_sigpig=(SCSCStatus.surveying, SCSCStatus.recruiting),
    join_sigpig=(SCSCStatus.surveying, SCSCStatus.recruiting)
)


async def update_scsc_global_status_ctrl(session: SessionDep, current_user_id: str, new_status: SCSCStatus, scsc_global_status: SCSCGlobalStatus) -> None:
    # VALIDATE SCSC GLOBAL STATUS UPDATE
    if (scsc_global_status.status, new_status) not in _valid_scsc_global_status_update: raise HTTPException(400, "invalid sig global status update")

    # end of inactive
    if scsc_global_status.status == SCSCStatus.inactive:
        for user in session.exec(select(User).where(User.status == UserStatus.pending, User.role == get_user_role_level("newcomer"))).all():
            user.status = UserStatus.banned
            session.add(user)
        for user in session.exec(select(User).where(User.status == UserStatus.pending, User.role == get_user_role_level("member"))).all():
            user_created_at_aware = user.created_at.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) - user_created_at_aware > timedelta(weeks=52 * 2):
                user.status = UserStatus.banned
                session.add(user)
            else:
                user.role = get_user_role_level("dormant")
                session.add(user)
                if user.discord_id: await change_discord_role(session, user.discord_id, 'dormant')
                
    
    # start of recruiting
    if new_status == SCSCStatus.recruiting:
        for sig in session.exec(select(SIG).where(SIG.status == SCSCStatus.surveying)).all():
            sig.status = SCSCStatus.recruiting
            session.add(sig)
        for pig in session.exec(select(PIG).where(PIG.status == SCSCStatus.surveying)).all():
            pig.status = SCSCStatus.recruiting
            session.add(pig)

    # end of active
    if scsc_global_status.status == SCSCStatus.active:
        # update previous semester data
        await send_discord_bot_request_no_reply(action_code=3008, body={"data": {"previousSemester": f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)}"}})
        # check if current semester archive category exists
        sig_res = await send_discord_bot_request(action_code=3005, body={'category_name': f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)} SIG Archive"})
        pig_res = await send_discord_bot_request(action_code=3005, body={'category_name': f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)} PIG Archive"})
        if not sig_res:
            await send_discord_bot_request_no_reply(action_code=3002, body={'category_name': f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)} SIG Archive"})
        if not pig_res:
            await send_discord_bot_request_no_reply(action_code=3004, body={'category_name': f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)} PIG Archive"})
        
        await process_igs(session, SIG, scsc_global_status)
        await process_igs(session, PIG, scsc_global_status)
        
        # update current semester
        scsc_global_status.year, scsc_global_status.semester = get_new_year_semester(scsc_global_status.year, scsc_global_status.semester)
        session.add(scsc_global_status)
        

    # start of inactive
    if new_status == SCSCStatus.inactive:
        for standby in session.exec(select(StandbyReqTbl)):
            session.delete(standby)
        for user in session.exec(select(User).where(User.status == UserStatus.active, User.role == get_user_role_level("newcomer"))).all():
            user.status = UserStatus.pending
            session.add(user)
        for user in session.exec(select(User).where(User.status == UserStatus.active, User.role == get_user_role_level("member"))).all():
            user.status = UserStatus.pending
            session.add(user)
        for applicant in session.exec(select(OldboyApplicant).where(OldboyApplicant.processed == False)).all():
            await process_oldboy_applicant_ctrl(session, applicant.id)
        
    
    # start of surveying
    if new_status == SCSCStatus.surveying:
        await send_discord_bot_request_no_reply(action_code=3002, body={'category_name': f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)} SIG Archive"})
        await send_discord_bot_request_no_reply(action_code=3004, body={'category_name': f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)} PIG Archive"})

    old_status = scsc_global_status.status
    scsc_global_status.status = new_status
    session.add(scsc_global_status)
    logger.info(f'info_type=scsc_global_status_updated ; old_status={old_status} ; new_status={new_status} ; executor={current_user_id}')
    session.commit()
    return
