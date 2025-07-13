from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlmodel import select

from src.db import SessionDep
from src.model import PIG, SIG, OldboyApplicant, SCSCGlobalStatus, SCSCStatus, User, UserStatus, StandbyReqTbl
from src.util import get_user_role_level, change_discord_role, send_discord_bot_request_no_reply

from .user import process_oldboy_applicant_ctrl

_valid_scsc_global_status_update = (
    (SCSCStatus.inactive, SCSCStatus.surveying),
    (SCSCStatus.surveying, SCSCStatus.recruiting),
    (SCSCStatus.recruiting, SCSCStatus.active),
    (SCSCStatus.active, SCSCStatus.surveying),
    (SCSCStatus.active, SCSCStatus.inactive),
)

_map_semester_name = {
    1: '1',
    2: 'S',
    3: '2',
    4: 'W',
}


@dataclass
class _CtrlStatusAvailable:
    create_sigpig: tuple[SCSCStatus, SCSCStatus]
    join_sigpig: tuple[SCSCStatus, SCSCStatus]


ctrl_status_available = _CtrlStatusAvailable(
    create_sigpig=(SCSCStatus.surveying, SCSCStatus.recruiting),
    join_sigpig=(SCSCStatus.surveying, SCSCStatus.recruiting)
)


async def update_scsc_global_status_ctrl(session: SessionDep, new_status: SCSCStatus, scsc_global_status: SCSCGlobalStatus) -> None:
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
        await send_discord_bot_request_no_reply(action_code=3008, body={"data": {"previousSemester": f"{scsc_global_status.year}-{_map_semester_name.get(scsc_global_status.semester)}"}})
        await send_discord_bot_request_no_reply(action_code=3002, body={'category_name': f"{scsc_global_status.year}-{_map_semester_name.get(scsc_global_status.semester)} SIG Archive"})
        await send_discord_bot_request_no_reply(action_code=3004, body={'category_name': f"{scsc_global_status.year}-{_map_semester_name.get(scsc_global_status.semester)} PIG Archive"})
        for sig in session.exec(select(SIG).where(SIG.year == scsc_global_status.year, SIG.semester == scsc_global_status.semester, SIG.status != SCSCStatus.inactive)).all():
            sig.status = SCSCStatus.inactive
            session.add(sig)
            await send_discord_bot_request_no_reply(action_code=4002, body={'sig_name': sig.title, "previous_semester": f"{scsc_global_status.year}-{_map_semester_name.get(scsc_global_status.semester)}"})
        for pig in session.exec(select(PIG).where(PIG.year == scsc_global_status.year, PIG.semester == scsc_global_status.semester, PIG.status != SCSCStatus.inactive)).all():
            pig.status = SCSCStatus.inactive
            session.add(pig)
            await send_discord_bot_request_no_reply(action_code=4004, body={'pig_name': pig.title, "previous_semester": f"{scsc_global_status.year}-{_map_semester_name.get(scsc_global_status.semester)}"})
        scsc_global_status.year += scsc_global_status.semester // 4
        scsc_global_status.semester = scsc_global_status.semester % 4 + 1
        session.add(scsc_global_status)

    # start of inactive
    if new_status == SCSCStatus.inactive:
        for standby in session.exec(select(StandbyReqTbl)):
            session.delete(standby)
        for user in session.exec(select(User).where(User.status == UserStatus.active, User.role == get_user_role_level("member"))).all():
            user.status = UserStatus.pending
            session.add(user)
        for applicant in session.exec(select(OldboyApplicant).where(OldboyApplicant.processed == False)).all():
            await process_oldboy_applicant_ctrl(session, applicant.id)
        

    scsc_global_status.status = new_status
    session.add(scsc_global_status)
    session.commit()
    return
