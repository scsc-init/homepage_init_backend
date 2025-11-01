import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Type

from fastapi import HTTPException
from sqlmodel import select

from src.db import SessionDep
from src.model import (
    PIG,
    SIG,
    OldboyApplicant,
    SCSCGlobalStatus,
    SCSCStatus,
    StandbyReqTbl,
    User,
    UserStatus,
)
from src.util import (
    change_discord_role,
    get_new_year_semester,
    get_user_role_level,
    map_semester_name,
    send_discord_bot_request,
    send_discord_bot_request_no_reply,
)

from .user import process_oldboy_applicant_ctrl

logger = logging.getLogger("app")

_valid_scsc_global_status_update = (
    (SCSCStatus.inactive, SCSCStatus.recruiting),
    (SCSCStatus.recruiting, SCSCStatus.active),
    (SCSCStatus.active, SCSCStatus.recruiting),
    (SCSCStatus.active, SCSCStatus.inactive),
)


@dataclass
class _CtrlStatusAvailable:
    create_sigpig: frozenset[SCSCStatus]
    join_sigpig: frozenset[SCSCStatus]  # also applied to leave
    join_sigpig_rolling_admission: frozenset[SCSCStatus]  # also applied to leave


ctrl_status_available = _CtrlStatusAvailable(
    create_sigpig=frozenset({SCSCStatus.recruiting}),
    join_sigpig=frozenset({SCSCStatus.recruiting}),
    join_sigpig_rolling_admission=frozenset({SCSCStatus.recruiting, SCSCStatus.active}),
)


async def _process_igs_change_semester(
    session: SessionDep, model: Type[SIG | PIG], scsc_global_status: SCSCGlobalStatus
):
    action_code, name_key = (4002, "sig_name") if model == SIG else (4004, "pig_name")
    igs = session.exec(
        select(model).where(
            model.year == scsc_global_status.year,
            model.semester == scsc_global_status.semester,
            model.status != SCSCStatus.inactive,
        )
    ).all()

    for ig in igs:
        try:
            if ig.should_extend:
                ig.year, ig.semester = get_new_year_semester(
                    scsc_global_status.year, scsc_global_status.semester
                )
                ig.status = SCSCStatus.recruiting
                session.add(ig)
            else:
                ig.status = SCSCStatus.inactive
                session.add(ig)
                await send_discord_bot_request_no_reply(
                    action_code=action_code,
                    body={
                        name_key: ig.title,
                        "previous_semester": f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)}",
                    },
                )
        except Exception as e:
            logger.error(
                f"err_type=process_igs ; ig_id={ig.id} ; ig_title={ig.title} ; msg=error processing {model.__name__}: {e}",
                exc_info=True,
            )


async def update_scsc_global_status_ctrl(
    session: SessionDep,
    current_user_id: str,
    new_status: SCSCStatus,
    scsc_global_status: SCSCGlobalStatus,
) -> None:
    # VALIDATE SCSC GLOBAL STATUS UPDATE
    if (scsc_global_status.status, new_status) not in _valid_scsc_global_status_update:
        raise HTTPException(400, "invalid sig global status update")

    # end of inactive
    if scsc_global_status.status == SCSCStatus.inactive:
        for user in session.exec(
            select(User).where(
                User.status == UserStatus.pending,
                User.role == get_user_role_level("newcomer"),
            )
        ).all():
            user.status = UserStatus.banned
            session.add(user)
        for user in session.exec(
            select(User).where(
                User.status == UserStatus.pending,
                User.role == get_user_role_level("member"),
            )
        ).all():
            user_created_at_aware = user.created_at.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) - user_created_at_aware > timedelta(
                weeks=52 * 2
            ):
                user.status = UserStatus.banned
                session.add(user)
            else:
                user.role = get_user_role_level("dormant")
                session.add(user)
                if user.discord_id:
                    await change_discord_role(session, user.discord_id, "dormant")

    # start of recruiting
    if new_status == SCSCStatus.recruiting:
        await send_discord_bot_request_no_reply(
            action_code=3002,
            body={
                "category_name": f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)} SIG Archive"
            },
        )
        await send_discord_bot_request_no_reply(
            action_code=3004,
            body={
                "category_name": f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)} PIG Archive"
            },
        )

    # start of active
    if new_status == SCSCStatus.active:
        for sig in session.exec(
            select(SIG).where(SIG.status == SCSCStatus.recruiting)
        ).all():
            sig.status = SCSCStatus.active
            session.add(sig)
        for pig in session.exec(
            select(PIG).where(PIG.status == SCSCStatus.recruiting)
        ).all():
            pig.status = SCSCStatus.active
            session.add(pig)

    # end of active
    if scsc_global_status.status == SCSCStatus.active:
        # update previous semester data
        await send_discord_bot_request_no_reply(
            action_code=3008,
            body={
                "data": {
                    "previousSemester": f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)}"
                }
            },
        )
        # check if current semester archive category exists
        sig_res = await send_discord_bot_request(
            action_code=3005,
            body={
                "category_name": f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)} SIG Archive"
            },
        )
        pig_res = await send_discord_bot_request(
            action_code=3005,
            body={
                "category_name": f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)} PIG Archive"
            },
        )
        if not sig_res:
            await send_discord_bot_request_no_reply(
                action_code=3002,
                body={
                    "category_name": f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)} SIG Archive"
                },
            )
        if not pig_res:
            await send_discord_bot_request_no_reply(
                action_code=3004,
                body={
                    "category_name": f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)} PIG Archive"
                },
            )

        await _process_igs_change_semester(session, SIG, scsc_global_status)
        await _process_igs_change_semester(session, PIG, scsc_global_status)

        # update current semester
        scsc_global_status.year, scsc_global_status.semester = get_new_year_semester(
            scsc_global_status.year, scsc_global_status.semester
        )
        session.add(scsc_global_status)

    # start of inactive
    if new_status == SCSCStatus.inactive:
        for standby in session.exec(select(StandbyReqTbl)):
            session.delete(standby)
        for user in session.exec(
            select(User).where(
                User.status == UserStatus.active,
                User.role == get_user_role_level("newcomer"),
            )
        ).all():
            user.status = UserStatus.pending
            session.add(user)
        for user in session.exec(
            select(User).where(
                User.status == UserStatus.active,
                User.role == get_user_role_level("member"),
            )
        ).all():
            user.status = UserStatus.pending
            session.add(user)
        for applicant in session.exec(
            select(OldboyApplicant).where(OldboyApplicant.processed == False)
        ).all():
            await process_oldboy_applicant_ctrl(session, applicant.id)

    old_status = scsc_global_status.status
    scsc_global_status.status = new_status
    session.add(scsc_global_status)
    logger.info(
        f"info_type=scsc_global_status_updated ; old_status={old_status} ; new_status={new_status} ; executor={current_user_id}"
    )
    session.commit()
    return
