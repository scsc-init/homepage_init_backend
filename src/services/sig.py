from typing import Annotated, Optional, Sequence

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.amqp import mq_client
from src.core import logger
from src.db import get_user_role_level
from src.model import SIG, SCSCGlobalStatus, SCSCStatus, SIGMember, SIGTag, Tag, User
from src.repositories import (
    SigMemberRepositoryDep,
    SigRepositoryDep,
    SigTagRepositoryDep,
    TagRepositoryDep,
    UserRepositoryDep,
)
from src.util import map_semester_name

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
        sig_tag_repository: SigTagRepositoryDep,
        tag_repository: TagRepositoryDep,
        user_repository: UserRepositoryDep,
    ) -> None:
        self.article_service = article_service
        self.sig_repository = sig_repository
        self.sig_member_repository = sig_member_repository
        self.sig_tag_repository = sig_tag_repository
        self.tag_repository = tag_repository
        self.user_repository = user_repository

    def _is_executive(self, user: User) -> bool:
        return user.role >= get_user_role_level("executive")

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
            created_year=scsc_global_status.year,
            created_semester=scsc_global_status.semester,
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
            if mq_client:
                await mq_client.send_discord_bot_request_no_reply(
                    action_code=4001,
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
        """
        Throws HTTPException with status 404 when no sig corresponding to the id found
        """
        sig = self.sig_repository.get_by_id(id)
        if not sig:
            raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
        return sig

    def get_sigs(
        self,
        year: Optional[int] = None,
        semester: Optional[int] = None,
        status: Optional[SCSCStatus] = None,
        tags: Sequence[str] | None = None,
    ) -> Sequence[SIG]:
        filters = {}
        if year is not None:
            filters["year"] = year
        if semester is not None:
            filters["semester"] = semester
        if status:
            filters["status"] = status

        return self.sig_repository.get_by_filters(filters, tags)

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
            if mq_client:
                await mq_client.send_discord_bot_request_no_reply(
                    action_code=4005, body=bot_body
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

        if mq_client:
            await mq_client.send_discord_bot_request_no_reply(
                action_code=4002,
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

    def get_members(self, id: int) -> Sequence[SIGMember]:
        """
        Throws HTTPException with status 404 when no sig corresponding to the id found
        """
        sig = self.get_by_id(id)
        return sig.members

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
            if mq_client:
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
            if mq_client:
                await mq_client.send_discord_bot_request_no_reply(
                    action_code=2001,
                    body={"user_id": user.discord_id, "role_name": sig.title},
                )

        logger.info(
            f"info_type=sig_join ; sig_id={sig.id} ; title={sig.title} ; executor_id={current_user.id} ; joined_user_id={body.user_id} ; year={sig.year} ; semester={sig.semester}"
        )

    async def leave_sig(self, id: int, executor: User) -> None:
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
        if sig.owner == executor.id:
            raise HTTPException(
                409, detail="시그/피그장은 해당 시그/피그를 탈퇴할 수 없습니다"
            )

        member = self.sig_member_repository.get_by_sig_and_user_id(id, executor.id)
        if not member:
            raise HTTPException(404, detail="시그/피그의 구성원이 아닙니다")

        self.sig_member_repository.delete(member)

        if executor.discord_id:
            if mq_client:
                await mq_client.send_discord_bot_request_no_reply(
                    action_code=2002,
                    body={"user_id": executor.discord_id, "role_name": sig.title},
                )

        logger.info(
            f"info_type=sig_leave ; {sig.id=} ; {sig.title=} ; {executor.id=} ; left_user_id={executor.id} ; {sig.year=} ; {sig.semester=}"
        )

    async def executive_leave_sig(
        self,
        id: int,
        executor: User,
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
            if mq_client:
                await mq_client.send_discord_bot_request_no_reply(
                    action_code=2002,
                    body={"user_id": user.discord_id, "role_name": sig.title},
                )

        logger.info(
            f"info_type=sig_leave ; {sig.id=} ; {sig.title=} ; {executor.id=} ; left_user_id={body.user_id} ; {sig.year=} ; {sig.semester=}"
        )

    def add_sig_tag(self, sig_id: int, tag_id: int, executor: User) -> SIGTag:
        sig = self.sig_repository.get_by_id(sig_id)
        if sig is None:
            raise HTTPException(404, detail=f"시그({sig_id=})가 존재하지 않습니다")

        is_executive = self._is_executive(executor)
        if not is_executive and sig.owner != executor.id:
            raise HTTPException(403, detail="타인의 시그에 태그를 추가할 수 없습니다")

        tag = self.tag_repository.get_by_id(tag_id)
        if tag is None:
            raise HTTPException(404, detail=f"태그({tag_id=})가 존재하지 않습니다")

        if tag.is_major and not is_executive:
            raise HTTPException(403, detail="major 태그는 운영진만 추가할 수 있습니다")

        try:
            sig_tag = self.sig_tag_repository.create(
                SIGTag(sig_id=sig_id, tag_id=tag_id)
            )
        except IntegrityError:
            raise HTTPException(409, detail="이미 추가된 태그입니다") from None

        logger.info(
            f"info_type=add_sig_tag ; sig_id={sig_id} ; tag_id={tag_id} ; executor_id={executor.id}"
        )
        return sig_tag

    def get_sig_tags(self, sig_id: int) -> Sequence[Tag]:
        sig = self.sig_repository.get_by_id(sig_id)
        if sig is None:
            raise HTTPException(404, detail=f"시그({sig_id=})가 존재하지 않습니다")

        return sorted(
            sig.tags,
            key=lambda tag: (not tag.is_major, tag.text),
        )

    def remove_sig_tag(self, sig_id: int, tag_id: int, executor: User) -> None:
        sig = self.sig_repository.get_by_id(sig_id)
        if sig is None:
            raise HTTPException(404, detail=f"시그({sig_id=})가 존재하지 않습니다")

        is_executive = self._is_executive(executor)
        if not is_executive and sig.owner != executor.id:
            raise HTTPException(403, detail="타인의 시그 태그를 삭제할 수 없습니다")

        tag = self.tag_repository.get_by_id(tag_id)
        if tag is None:
            raise HTTPException(404, detail=f"태그({tag_id=})가 존재하지 않습니다")

        if tag.is_major and not is_executive:
            raise HTTPException(403, detail="major 태그는 운영진만 삭제할 수 있습니다")

        sig_tag = self.sig_tag_repository.get_by_sig_id_and_tag_id(sig_id, tag_id)
        if sig_tag is None:
            raise HTTPException(404, detail="해당 시그에 연결된 태그가 없습니다")

        self.sig_tag_repository.delete(sig_tag)

        if not tag.is_major and self.sig_tag_repository.count_by_tag_id(tag_id) == 0:
            self.sig_tag_repository.delete_by_tag_id(tag_id)
            self.tag_repository.delete(tag)

        logger.info(
            f"info_type=remove_sig_tag ; sig_id={sig_id} ; tag_id={tag_id} ; executor_id={executor.id}"
        )

    def get_tags(self) -> Sequence[Tag]:
        return self.tag_repository.get_all()

    def _create_tag(self, text: str, is_major: bool, executor: User) -> Tag:
        normalized_text = text.strip()
        if not normalized_text:
            raise HTTPException(422, detail="태그명은 비어 있을 수 없습니다")

        existing = self.tag_repository.get_by_text(normalized_text)
        if existing is not None:
            raise HTTPException(409, detail="이미 존재하는 태그입니다")

        try:
            tag = self.tag_repository.create(
                Tag(text=normalized_text, is_major=is_major)
            )
        except IntegrityError:
            raise HTTPException(409, detail="이미 존재하는 태그입니다") from None

        logger.info(
            f"info_type=create_tag ; tag_id={tag.id} ; text={tag.text} ; is_major={tag.is_major} ; executor_id={executor.id}"
        )
        return tag

    def create_tag_by_user(self, text: str, executor: User) -> Tag:
        return self._create_tag(text, False, executor)

    def create_tag_by_executive(self, text: str, is_major: bool, executor: User) -> Tag:
        return self._create_tag(text, is_major, executor)

    def delete_tag(self, tag_id: int, executor: User) -> None:
        tag = self.tag_repository.get_by_id(tag_id)
        if tag is None:
            raise HTTPException(404, detail=f"태그({tag_id=})가 존재하지 않습니다")

        self.tag_repository.delete(tag)

        logger.info(
            f"info_type=delete_tag ; tag_id={tag_id} ; executor_id={executor.id}"
        )


SigServiceDep = Annotated[SigService, Depends()]
