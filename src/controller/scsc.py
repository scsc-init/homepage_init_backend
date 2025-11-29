from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Annotated, Type

from fastapi import Depends, HTTPException
from pydantic import BaseModel

from src.core import logger
from src.db import SessionDep
from src.dependencies import SCSCGlobalStatusDep
from src.model import (
    PIG,
    SIG,
    SCSCGlobalStatus,
    SCSCStatus,
    UserStatus,
)
from src.repositories import (
    OldboyApplicantRepositoryDep,
    PigRepositoryDep,
    SigRepositoryDep,
    StandbyReqTblRepositoryDep,
    UserRepositoryDep,
)
from src.util import (
    get_new_year_semester,
    get_user_role_level,
    map_semester_name,
    send_discord_bot_request,
    send_discord_bot_request_no_reply,
)

from .user import OldboyServiceDep, UserServiceDep

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
    create_sigpig=frozenset({SCSCStatus.recruiting, SCSCStatus.active}),
    join_sigpig=frozenset({SCSCStatus.recruiting}),
    join_sigpig_rolling_admission=frozenset({SCSCStatus.recruiting, SCSCStatus.active}),
)


class BodyUpdateSCSCGlobalStatus(BaseModel):
    status: SCSCStatus


class SCSCService:
    def __init__(
        self,
        session: SessionDep,
        scsc_global_status: SCSCGlobalStatusDep,
        user_service: UserServiceDep,
        oldboy_service: OldboyServiceDep,
        sig_repository: SigRepositoryDep,
        pig_repository: PigRepositoryDep,
        user_repository: UserRepositoryDep,
        standby_repository: StandbyReqTblRepositoryDep,
        oldboy_repository: OldboyApplicantRepositoryDep,
    ):
        self.session = session
        self.scsc_global_status = scsc_global_status
        self.user_service = user_service
        self.oldboy_service = oldboy_service
        self.sig_repo = sig_repository
        self.pig_repo = pig_repository
        self.user_repo = user_repository
        self.standby_repo = standby_repository
        self.oldboy_repo = oldboy_repository

    def get_global_status(self) -> SCSCGlobalStatus:
        return self.scsc_global_status

    def get_all_statuses(self) -> dict[str, list[str]]:
        return {"statuses": ["recruiting", "active", "inactive"]}

    async def _process_igs_change_semester(
        self, model: Type[SIG | PIG], scsc_global_status: SCSCGlobalStatus
    ):
        action_code, name_key = (
            (4002, "sig_name") if model == SIG else (4004, "pig_name")
        )

        repo = self.sig_repo if model == SIG else self.pig_repo
        igs = repo.get_by_year_semester_not_inactive(
            scsc_global_status.year, scsc_global_status.semester
        )

        for ig in igs:
            try:
                if ig.should_extend:
                    ig.year, ig.semester = get_new_year_semester(
                        scsc_global_status.year, scsc_global_status.semester
                    )
                    ig.status = SCSCStatus.recruiting
                    self.session.add(ig)
                else:
                    ig.status = SCSCStatus.inactive
                    self.session.add(ig)
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

    async def update_global_status(
        self,
        current_user_id: str,
        new_status: SCSCStatus,
    ) -> None:
        scsc_global_status = self.scsc_global_status

        if (
            scsc_global_status.status,
            new_status,
        ) not in _valid_scsc_global_status_update:
            raise HTTPException(400, "invalid sig global status update")

        # end of inactive
        if scsc_global_status.status == SCSCStatus.inactive:
            newcomers = self.user_repo.get_by_status_and_role(
                UserStatus.pending, get_user_role_level("newcomer")
            )
            for user in newcomers:
                user.status = UserStatus.banned
                self.session.add(user)

            members = self.user_repo.get_by_status_and_role(
                UserStatus.pending, get_user_role_level("member")
            )
            for user in members:
                user_created_at_aware = user.created_at.replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) - user_created_at_aware > timedelta(
                    weeks=52 * 2
                ):
                    user.status = UserStatus.banned
                    self.session.add(user)
                else:
                    user.role = get_user_role_level("dormant")
                    self.session.add(user)
                    if user.discord_id:
                        await self.user_service.change_discord_role(
                            user.discord_id, "dormant"
                        )

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
            recruiting_sigs = self.sig_repo.get_by_status(SCSCStatus.recruiting)
            for sig in recruiting_sigs:
                sig.status = SCSCStatus.active
                self.session.add(sig)

            recruiting_pigs = self.pig_repo.get_by_status(SCSCStatus.recruiting)
            for pig in recruiting_pigs:
                pig.status = SCSCStatus.active
                self.session.add(pig)

        # end of active
        if scsc_global_status.status == SCSCStatus.active:
            await send_discord_bot_request_no_reply(
                action_code=3008,
                body={
                    "data": {
                        "previousSemester": f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)}"
                    }
                },
            )
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

            await self._process_igs_change_semester(SIG, scsc_global_status)
            await self._process_igs_change_semester(PIG, scsc_global_status)

            scsc_global_status.year, scsc_global_status.semester = (
                get_new_year_semester(
                    scsc_global_status.year, scsc_global_status.semester
                )
            )
            self.session.add(scsc_global_status)

        # start of inactive
        if new_status == SCSCStatus.inactive:
            standbys = self.standby_repo.list_all()
            for standby in standbys:
                self.session.delete(standby)

            active_newcomers = self.user_repo.get_by_status_and_role(
                UserStatus.active, get_user_role_level("newcomer")
            )
            for user in active_newcomers:
                user.status = UserStatus.pending
                self.session.add(user)

            active_members = self.user_repo.get_by_status_and_role(
                UserStatus.active, get_user_role_level("member")
            )
            for user in active_members:
                user.status = UserStatus.pending
                self.session.add(user)

            unprocessed_applicants = self.oldboy_repo.get_unprocessed()
            for applicant in unprocessed_applicants:
                await self.oldboy_service.process_applicant(applicant.id)

        old_status = scsc_global_status.status
        scsc_global_status.status = new_status
        self.session.add(scsc_global_status)

        logger.info(
            f"info_type=scsc_global_status_updated ; old_status={old_status} ; new_status={new_status} ; executor={current_user_id}"
        )
        self.session.commit()


SCSCServiceDep = Annotated[SCSCService, Depends()]
