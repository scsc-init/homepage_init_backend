from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlmodel import select

from src.db import SessionDep
from src.model import SIG, PIG, SCSCGlobalStatus, SCSCStatus, User, UserStatus, OldboyApplicant
from src.util import get_user_role_level

from .user import process_oldboy_applicant_ctrl

_valid_scsc_global_status_update = (
    (SCSCStatus.inactive, SCSCStatus.surveying),
    (SCSCStatus.surveying, SCSCStatus.recruiting),
    (SCSCStatus.recruiting, SCSCStatus.active),
    (SCSCStatus.active, SCSCStatus.surveying),
    (SCSCStatus.active, SCSCStatus.inactive),
)

status_available_create_sigpig = (SCSCStatus.surveying, SCSCStatus.recruiting)
status_available_join_sigpig = (SCSCStatus.surveying, SCSCStatus.recruiting)


def _check_valid_scsc_global_status_update(old_status: SCSCStatus, new_status: SCSCStatus) -> bool:
    for valid_update in _valid_scsc_global_status_update:
        if (old_status, new_status) == valid_update: return True
    return False


async def update_scsc_global_status_ctrl(session: SessionDep, new_status: SCSCStatus, scsc_global_status: SCSCGlobalStatus) -> None:
    if not _check_valid_scsc_global_status_update(scsc_global_status.status, new_status): raise HTTPException(400, "invalid sig global status update")

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
        for sig in session.exec(select(SIG).where(SIG.year == scsc_global_status.year, SIG.semester == scsc_global_status.semester, SIG.status != SCSCStatus.inactive)).all():
            sig.status = SCSCStatus.inactive
            session.add(sig)
        for pig in session.exec(select(PIG).where(PIG.year == scsc_global_status.year, PIG.semester == scsc_global_status.semester, PIG.status != SCSCStatus.inactive)).all():
            pig.status = SCSCStatus.inactive
            session.add(pig)
        if scsc_global_status.semester != 4: scsc_global_status.semester += 1
        else:
            scsc_global_status.semester = 1
            scsc_global_status.year += 1
        session.add(scsc_global_status)

    # start of inactive
    if new_status == SCSCStatus.inactive:
        for user in session.exec(select(User).where(User.status == UserStatus.active, User.role == get_user_role_level("member"))).all():
            user.status = UserStatus.pending
            session.add(user)
        for applicant in session.exec(select(OldboyApplicant).where(OldboyApplicant.processed == False)).all():
            await process_oldboy_applicant_ctrl(session, applicant.id)

    scsc_global_status.status = new_status
    session.add(scsc_global_status)
    session.commit()
    return
