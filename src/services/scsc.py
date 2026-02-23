from dataclasses import dataclass
from typing import Annotated, Type

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import case, exists, select, update

from src.amqp import mq_client
from src.core import logger
from src.db import SessionDep, backup_db_before_status_change, get_user_role_level
from src.dependencies import SCSCGlobalStatusDep
from src.model import PIG, SIG, Enrollment, SCSCGlobalStatus, SCSCStatus, User
from src.repositories import (
    OldboyApplicantRepositoryDep,
    PigRepositoryDep,
    SigRepositoryDep,
    StandbyReqTblRepositoryDep,
    UserRepositoryDep,
)
from src.util import (
    get_next_year_semester,
    map_semester_name,
)

from .key_value import KvServiceDep
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
        kv_service: KvServiceDep,
    ):
        self.session = session
        self.scsc_global_status = scsc_global_status
        self.user_service = user_service
        self.oldboy_service = oldboy_service
        self.sig_repository = sig_repository
        self.pig_repository = pig_repository
        self.user_repository = user_repository
        self.standby_repository = standby_repository
        self.oldboy_repository = oldboy_repository
        self.kv_service = kv_service

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

        repo = self.sig_repository if model == SIG else self.pig_repository
        igs = repo.get_by_year_semester_not_inactive(
            scsc_global_status.year, scsc_global_status.semester
        )

        for ig in igs:
            try:
                if ig.should_extend:
                    ig.year, ig.semester = get_next_year_semester(
                        scsc_global_status.year, scsc_global_status.semester
                    )
                    ig.status = SCSCStatus.recruiting
                    self.session.add(ig)
                else:
                    ig.status = SCSCStatus.inactive
                    self.session.add(ig)
                    await mq_client.send_discord_bot_request_no_reply(
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

        enrollment_grant_until = self.kv_service.get_enrollment_grant_until()
        if scsc_global_status.status == SCSCStatus.active:
            if (
                scsc_global_status.year,
                scsc_global_status.semester,
            ) >= enrollment_grant_until:
                raise HTTPException(
                    412, "set valid enrollment grant policy before change semester"
                )

        try:
            backup_db_before_status_change(scsc_global_status)
        except Exception as exc:
            logger.error(
                "err_type=db_backup ; msg=failed to back up database before status change",
                exc_info=True,
            )
            raise HTTPException(
                status_code=500,
                detail="failed to back up database before status change",
            ) from exc

        # start of recruiting
        if new_status == SCSCStatus.recruiting:
            await mq_client.send_discord_bot_request_no_reply(
                action_code=3002,
                body={
                    "category_name": f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)} SIG Archive"
                },
            )
            await mq_client.send_discord_bot_request_no_reply(
                action_code=3004,
                body={
                    "category_name": f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)} PIG Archive"
                },
            )

        # start of active
        if new_status == SCSCStatus.active:
            recruiting_sigs = self.sig_repository.get_by_status(SCSCStatus.recruiting)
            for sig in recruiting_sigs:
                sig.status = SCSCStatus.active
                self.session.add(sig)

            recruiting_pigs = self.pig_repository.get_by_status(SCSCStatus.recruiting)
            for pig in recruiting_pigs:
                pig.status = SCSCStatus.active
                self.session.add(pig)

        # end of active
        if scsc_global_status.status == SCSCStatus.active:
            await mq_client.send_discord_bot_request_no_reply(
                action_code=3008,
                body={
                    "data": {
                        "previousSemester": f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)}"
                    }
                },
            )
            sig_res = await mq_client.send_discord_bot_request(
                action_code=3005,
                body={
                    "category_name": f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)} SIG Archive"
                },
            )
            pig_res = await mq_client.send_discord_bot_request(
                action_code=3005,
                body={
                    "category_name": f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)} PIG Archive"
                },
            )
            if not sig_res:
                await mq_client.send_discord_bot_request_no_reply(
                    action_code=3002,
                    body={
                        "category_name": f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)} SIG Archive"
                    },
                )
            if not pig_res:
                await mq_client.send_discord_bot_request_no_reply(
                    action_code=3004,
                    body={
                        "category_name": f"{scsc_global_status.year}-{map_semester_name.get(scsc_global_status.semester)} PIG Archive"
                    },
                )

            await self._process_igs_change_semester(SIG, scsc_global_status)
            await self._process_igs_change_semester(PIG, scsc_global_status)

            next_year, next_semester = get_next_year_semester(
                scsc_global_status.year, scsc_global_status.semester
            )

            enrolled_exists = exists(
                select(Enrollment.id).where(
                    Enrollment.year == next_year,
                    Enrollment.semester == next_semester,
                    Enrollment.user_id == User.id,
                )
            )
            self.session.execute(
                update(User)
                .where(~User.is_banned, User.role <= get_user_role_level("member"))
                .values(is_active=case((enrolled_exists, True), else_=False))
                .execution_options(synchronize_session=False)
            )
            self.standby_repository.delete_all()

        # start of inactive (regular semester starts)
        if new_status == SCSCStatus.inactive:
            unprocessed_applicants = self.oldboy_repository.get_unprocessed()
            for applicant in unprocessed_applicants:
                await self.oldboy_service.process_applicant(applicant.id)

            self.session.execute(
                update(User)
                .where(
                    ~User.is_active,
                    ~User.is_banned,
                    User.role <= get_user_role_level("member"),
                )
                .values(role=get_user_role_level("dormant"))
                .execution_options(synchronize_session=False)
            )

        # update the scsc global status
        if scsc_global_status.status == SCSCStatus.active:
            scsc_global_status.year, scsc_global_status.semester = (
                get_next_year_semester(
                    scsc_global_status.year, scsc_global_status.semester
                )
            )
            self.session.add(scsc_global_status)
        old_status = scsc_global_status.status
        scsc_global_status.status = new_status
        self.session.add(scsc_global_status)

        logger.info(
            f"info_type=scsc_global_status_updated ; old_status={old_status} ; new_status={new_status} ; executor={current_user_id}"
        )
        self.session.commit()


SCSCServiceDep = Annotated[SCSCService, Depends()]
