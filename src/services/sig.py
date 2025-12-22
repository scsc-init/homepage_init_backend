from typing import Annotated, Optional, Sequence

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.amqp import mq_client
from src.core import logger
from src.model import SIG, SCSCGlobalStatus, SCSCStatus, SIGMember, User
from src.repositories import SigMemberRepositoryDep, SigRepositoryDep, UserRepositoryDep
from src.schemas import SigMemberResponse, UserResponse
from src.util import (
    get_user_role_level,
    map_semester_name,
)

from .article import ArticleServiceDep, BodyCreateArticle
from .scsc import ctrl_status_available


class BodyCreateSIG(BaseModel):
    title: str
    description: str
    content: str
    is_rolling_admission: bool = False


class BodyUpdateSIG(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    status: Optional[SCSCStatus] = None
    should_extend: Optional[bool] = None
    is_rolling_admission: Optional[bool] = None


class BodyHandoverSIG(BaseModel):
    new_owner: str


class BodyExecutiveJoinSIG(BaseModel):
    user_id: str


class BodyExecutiveLeaveSIG(BaseModel):
    user_id: str


class SigService:
    def __init__(
        self,
        article_service: ArticleServiceDep,
        sig_repository: SigRepositoryDep,
        sig_member_repository: SigMemberRepositoryDep,
        user_repository: UserRepositoryDep,
    ) -> None:
        self.article_service = article_service
        self.sig_repository = sig_repository
        self.sig_member_repository = sig_member_repository
        self.user_repository = user_repository

    async def create_sig(
        self,
        scsc_global_status: SCSCGlobalStatus,
        current_user: User,
        body: BodyCreateSIG,
    ) -> SIG:
        if scsc_global_status.status not in ctrl_status_available.create_sigpig:
            raise HTTPException(
                400,
                f"SCSC 전역 상태가 {ctrl_status_available.create_sigpig}일 때만 시그/피그를 생성할 수 있습니다",
            )

        sig_article = await self.article_service.create_article(
            BodyCreateArticle(title=body.title, content=body.content, board_id=1),
            current_user.id,
            get_user_role_level("president"),
        )

        sig = SIG(
            title=body.title,
            description=body.description,
            content_id=sig_article.id,
            year=scsc_global_status.year,
            semester=scsc_global_status.semester,
            owner=current_user.id,
            status=scsc_global_status.status,
            is_rolling_admission=body.is_rolling_admission,
        )

        try:
            sig = self.sig_repository.create(sig)
        except IntegrityError:
            raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")

        if sig.id is None:
            raise HTTPException(503, detail="sig primary key does not exist")

        sig_member = SIGMember(ig_id=sig.id, user_id=current_user.id)
        try:
            self.sig_member_repository.create(sig_member)
        except IntegrityError as exc:
            logger.info(exc.orig)
            raise HTTPException(
                409, detail="시그/피그장 자동 가입 중 중복 오류가 발생했습니다"
            ) from exc

        if current_user.discord_id:
            await mq_client.send_discord_bot_request_no_reply(
                action_code=4003,
                body={
                    "sig_name": sig.title,
                    "user_id_list": [current_user.discord_id],
                    "sig_description": sig.description,
                },
            )

        logger.info(
            f"info_type=sig_created ; sig_id={sig.id} ; title={sig.title} ; owner_id={current_user.id} ; year={sig.year} ; semester={sig.semester} ; is_rolling_admission={sig.is_rolling_admission}"
        )
        return sig

    def get_by_id(self, id: int) -> SIG:
        sig = self.sig_repository.get_by_id(id)
        if not sig:
            raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
        return sig

    def get_all(self) -> Sequence[SIG]:
        return self.sig_repository.list_all()

    async def update_sig(
        self,
        id: int,
        current_user: User,
        body: BodyUpdateSIG,
        is_executive: bool,
    ) -> None:
        sig = self.sig_repository.get_by_id(id)
        if not sig:
            raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")

        if not is_executive and sig.owner != current_user.id:
            raise HTTPException(
                status_code=403, detail="타인의 시그/피그를 변경할 수 없습니다"
            )

        old_title = sig.title

        if body.title:
            sig.title = body.title
        if body.description:
            sig.description = body.description

        if body.content:
            sig_article = await self.article_service.create_article(
                BodyCreateArticle(title=sig.title, content=body.content, board_id=1),
                current_user.id,
                get_user_role_level("president"),
            )
            sig.content_id = sig_article.id

        if body.status:
            if not is_executive:
                raise HTTPException(403, detail="관리자 이상의 권한이 필요합니다")
            sig.status = body.status

        if body.should_extend is not None:
            sig.should_extend = body.should_extend
        if body.is_rolling_admission is not None:
            sig.is_rolling_admission = body.is_rolling_admission

        try:
            self.sig_repository.update(sig)
        except IntegrityError:
            raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")

        bot_body = {}
        bot_body["sig_name"] = old_title
        if body.title:
            bot_body["new_sig_name"] = body.title
        if body.description:
            bot_body["new_topic"] = body.description
        if len(bot_body) > 1:
            await mq_client.send_discord_bot_request_no_reply(
                action_code=4006, body=bot_body
            )

        logger.info(
            f"info_type=sig_updated ; sig_id={id} ; title={sig.title} ; revisioner_id={current_user.id} ; year={sig.year} ; semester={sig.semester} ; is_rolling_admission={sig.is_rolling_admission}"
        )

    async def delete_sig(
        self,
        id: int,
        current_user: User,
        is_executive: bool,
    ) -> None:
        sig = self.get_by_id(id)

        if not is_executive and sig.owner != current_user.id:
            raise HTTPException(403, detail="타인의 시그/피그를 삭제할 수 없습니다")

        if sig.status == SCSCStatus.inactive:
            raise HTTPException(400, detail="해당 시그/피그는 이미 비활성 상태입니다")

        sig.status = SCSCStatus.inactive
        self.sig_repository.update(sig)

        await mq_client.send_discord_bot_request_no_reply(
            action_code=4004,
            body={
                "sig_name": sig.title,
                "previous_semester": f"{sig.year}-{map_semester_name.get(sig.semester)}",
            },
        )

        logger.info(
            f"info_type=sig_deleted ; sig_id={sig.id} ; remover_id={current_user.id}"
        )

    def _handover_sig_ctrl(
        self, sig: SIG, new_owner_id: str, executor_id: str, is_forced: bool
    ) -> SIG:
        if sig.owner == new_owner_id:
            raise HTTPException(
                status_code=400,
                detail="새로운 시그/피그장은 현재 시그/피그장과 달라야 합니다",
            )

        new_owner_user = self.user_repository.get_by_id(new_owner_id)
        if not new_owner_user:
            raise HTTPException(
                status_code=404,
                detail="새로운 시그/피그장에 해당하는 사용자가 없습니다",
            )

        member = self.sig_member_repository.get_by_sig_and_user_id(sig.id, new_owner_id)
        if member is None:
            raise HTTPException(
                status_code=404,
                detail="새로운 시그/피그장은 해당 시그/피그의 구성원이어야 합니다",
            )

        old_owner = sig.owner
        sig.owner = new_owner_id
        self.sig_repository.update(sig)

        handover_type = "forced" if is_forced else "voluntary"
        logger.info(
            f"info_type=sig_handover ; handover_type={handover_type} ; sig_id={sig.id} ; title={sig.title} ; "
            f"executor_id={executor_id} ; old_owner_id={old_owner} ; new_owner_id={new_owner_id} ; "
            f"year={sig.year} ; semester={sig.semester}"
        )

        return sig

    def handover_sig(
        self,
        id: int,
        current_user: User,
        body: BodyHandoverSIG,
        is_executive: bool,
    ):
        sig = self.get_by_id(id)
        if not is_executive and current_user.id != sig.owner:
            raise HTTPException(403, detail="타인의 시그/피그를 변경할 수 없습니다")
        self._handover_sig_ctrl(sig, body.new_owner, current_user.id, is_executive)

    def get_members(self, id: int) -> Sequence[SigMemberResponse]:
        self.get_by_id(id)

        members = self.sig_member_repository.get_members_by_sig_id(id)
        res: list[SigMemberResponse] = []
        for member in members:
            user = self.user_repository.get_by_id(member.user_id)

            user_response = None
            if user:
                user_response = UserResponse.model_validate(user)

            member_response = SigMemberResponse(
                id=member.id,
                ig_id=member.ig_id,
                user_id=member.user_id,
                created_at=member.created_at,
                user=user_response,
            )
            res.append(member_response)

        return res

    async def join_sig(self, id: int, current_user: User) -> None:
        sig = self.get_by_id(id)
        allowed = (
            ctrl_status_available.join_sigpig_rolling_admission
            if sig.is_rolling_admission
            else ctrl_status_available.join_sigpig
        )
        if sig.status not in allowed:
            raise HTTPException(
                400, f"시그/피그 상태가 {allowed}일 때만 시그/피그에 가입할 수 있습니다"
            )

        sig_member = SIGMember(ig_id=id, user_id=current_user.id)
        try:
            self.sig_member_repository.create(sig_member)
        except IntegrityError:
            raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")

        if current_user.discord_id:
            await mq_client.send_discord_bot_request_no_reply(
                action_code=2001,
                body={"user_id": current_user.discord_id, "role_name": sig.title},
            )

        logger.info(
            f"info_type=sig_join ; sig_id={sig.id} ; title={sig.title} ; executor_id={current_user.id} ; joined_user_id={current_user.id} ; year={sig.year} ; semester={sig.semester}"
        )

    async def executive_join_sig(
        self,
        id: int,
        current_user: User,
        body: BodyExecutiveJoinSIG,
    ) -> None:
        sig = self.get_by_id(id)
        user = self.user_repository.get_by_id(body.user_id)
        if not user:
            raise HTTPException(404, detail="해당 id의 사용자가 없습니다")

        sig_member = SIGMember(ig_id=id, user_id=body.user_id)
        try:
            self.sig_member_repository.create(sig_member)
        except IntegrityError:
            raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")

        if user.discord_id:
            await mq_client.send_discord_bot_request_no_reply(
                action_code=2001,
                body={"user_id": user.discord_id, "role_name": sig.title},
            )

        logger.info(
            f"info_type=sig_join ; sig_id={sig.id} ; title={sig.title} ; executor_id={current_user.id} ; joined_user_id={body.user_id} ; year={sig.year} ; semester={sig.semester}"
        )

    async def leave_sig(self, id: int, current_user: User) -> None:
        sig = self.get_by_id(id)
        allowed = (
            ctrl_status_available.join_sigpig_rolling_admission
            if sig.is_rolling_admission
            else ctrl_status_available.join_sigpig
        )
        if sig.status not in allowed:
            raise HTTPException(
                400,
                f"시그/피그 상태가 {allowed}일 때만 시그/피그에서 탈퇴할 수 있습니다",
            )
        if sig.owner == current_user.id:
            raise HTTPException(
                409, detail="시그/피그장은 해당 시그/피그를 탈퇴할 수 없습니다"
            )

        member = self.sig_member_repository.get_by_sig_and_user_id(id, current_user.id)
        if not member:
            raise HTTPException(404, detail="시그/피그의 구성원이 아닙니다")

        self.sig_member_repository.delete(member)

        if current_user.discord_id:
            await mq_client.send_discord_bot_request_no_reply(
                action_code=2002,
                body={"user_id": current_user.discord_id, "role_name": sig.title},
            )

        logger.info(
            f"info_type=sig_leave ; sig_id={sig.id} ; title={sig.title} ; executor_id={current_user.id} ; left_user_id={current_user.id} ; year={sig.year} ; semester={sig.semester}"
        )

    async def executive_leave_sig(
        self,
        id: int,
        current_user: User,
        body: BodyExecutiveLeaveSIG,
    ) -> None:
        sig = self.get_by_id(id)
        user = self.user_repository.get_by_id(body.user_id)
        if not user:
            raise HTTPException(404, detail="해당 id의 사용자가 없습니다")

        if sig.owner == user.id:
            raise HTTPException(
                409, detail="시그/피그장은 해당 시그/피그를 탈퇴할 수 없습니다"
            )

        member = self.sig_member_repository.get_by_sig_and_user_id(id, body.user_id)
        if not member:
            raise HTTPException(404, detail="시그/피그의 구성원이 아닙니다")

        self.sig_member_repository.delete(member)

        if user.discord_id:
            await mq_client.send_discord_bot_request_no_reply(
                action_code=2002,
                body={"user_id": user.discord_id, "role_name": sig.title},
            )

        logger.info(
            f"info_type=sig_leave ; sig_id={sig.id} ; title={sig.title} ; executor_id={current_user.id} ; left_user_id={body.user_id} ; year={sig.year} ; semester={sig.semester}"
        )


SigServiceDep = Annotated[SigService, Depends()]
