from typing import Annotated, Optional, Sequence

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.core import logger
from src.model import PIG, PIGMember, SCSCGlobalStatus, SCSCStatus, User
from src.repositories import PigMemberRepositoryDep, PigRepositoryDep, UserRepositoryDep
from src.schemas import PigMemberResponse, UserResponse
from src.util import (
    get_user_role_level,
    map_semester_name,
    send_discord_bot_request_no_reply,
)

from .article import ArticleServiceDep, BodyCreateArticle
from .scsc import ctrl_status_available


class BodyCreatePIG(BaseModel):
    title: str
    description: str
    content: str
    is_rolling_admission: bool = False


class BodyUpdatePIG(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    status: Optional[SCSCStatus] = None
    should_extend: Optional[bool] = None
    is_rolling_admission: Optional[bool] = None


class BodyHandoverPIG(BaseModel):
    new_owner: str


class BodyExecutiveJoinPIG(BaseModel):
    user_id: str


class BodyExecutiveLeavePIG(BaseModel):
    user_id: str


class PigService:
    def __init__(
        self,
        article_service: ArticleServiceDep,
        pig_repository: PigRepositoryDep,
        pig_member_repository: PigMemberRepositoryDep,
        user_repository: UserRepositoryDep,
    ) -> None:
        self.article_service = article_service
        self.pig_repository = pig_repository
        self.pig_member_repository = pig_member_repository
        self.user_repository = user_repository

    async def create_pig(
        self,
        scsc_global_status: SCSCGlobalStatus,
        current_user: User,
        body: BodyCreatePIG,
    ) -> PIG:
        if scsc_global_status.status not in ctrl_status_available.create_sigpig:
            raise HTTPException(
                400,
                f"SCSC 전역 상태가 {ctrl_status_available.create_sigpig}일 때만 시그/피그를 생성할 수 있습니다",
            )

        pig_article = await self.article_service.create_article(
            BodyCreateArticle(title=body.title, content=body.content, board_id=1),
            current_user.id,
            get_user_role_level("president"),
        )

        pig = PIG(
            title=body.title,
            description=body.description,
            content_id=pig_article.id,
            year=scsc_global_status.year,
            semester=scsc_global_status.semester,
            owner=current_user.id,
            status=scsc_global_status.status,
            is_rolling_admission=body.is_rolling_admission,
        )

        try:
            pig = self.pig_repository.create(pig)
        except IntegrityError:
            raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")

        if pig.id is None:
            raise HTTPException(503, detail="pig primary key does not exist")

        pig_member = PIGMember(ig_id=pig.id, user_id=current_user.id)
        try:
            self.pig_member_repository.create(pig_member)
        except IntegrityError as exc:
            logger.info(exc.orig)
            raise HTTPException(
                409, detail="시그/피그장 자동 가입 중 중복 오류가 발생했습니다"
            ) from exc

        if current_user.discord_id:
            await send_discord_bot_request_no_reply(
                action_code=4003,
                body={
                    "pig_name": pig.title,
                    "user_id_list": [current_user.discord_id],
                    "pig_description": pig.description,
                },
            )

        logger.info(
            f"info_type=pig_created ; pig_id={pig.id} ; title={pig.title} ; owner_id={current_user.id} ; year={pig.year} ; semester={pig.semester} ; is_rolling_admission={pig.is_rolling_admission}"
        )
        return pig

    def get_by_id(self, id: int) -> PIG:
        pig = self.pig_repository.get_by_id(id)
        if not pig:
            raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
        return pig

    def get_all(self) -> Sequence[PIG]:
        return self.pig_repository.list_all()

    async def update_pig(
        self,
        id: int,
        current_user: User,
        body: BodyUpdatePIG,
        is_executive: bool,
    ) -> None:
        pig = self.pig_repository.get_by_id(id)
        if not pig:
            raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")

        if not is_executive and pig.owner != current_user.id:
            raise HTTPException(
                status_code=403, detail="타인의 시그/피그를 변경할 수 없습니다"
            )

        old_title = pig.title

        if body.title:
            pig.title = body.title
        if body.description:
            pig.description = body.description

        if body.content:
            pig_article = await self.article_service.create_article(
                BodyCreateArticle(title=pig.title, content=body.content, board_id=1),
                current_user.id,
                get_user_role_level("president"),
            )
            pig.content_id = pig_article.id

        if body.status:
            if not is_executive:
                raise HTTPException(403, detail="관리자 이상의 권한이 필요합니다")
            pig.status = body.status

        if body.should_extend is not None:
            pig.should_extend = body.should_extend
        if body.is_rolling_admission is not None:
            pig.is_rolling_admission = body.is_rolling_admission

        try:
            self.pig_repository.update(pig)
        except IntegrityError:
            raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")

        bot_body = {}
        bot_body["pig_name"] = old_title
        if body.title:
            bot_body["new_pig_name"] = body.title
        if body.description:
            bot_body["new_topic"] = body.description
        if len(bot_body) > 1:
            await send_discord_bot_request_no_reply(action_code=4006, body=bot_body)

        logger.info(
            f"info_type=pig_updated ; pig_id={id} ; title={pig.title} ; revisioner_id={current_user.id} ; year={pig.year} ; semester={pig.semester} ; is_rolling_admission={pig.is_rolling_admission}"
        )

    async def delete_pig(
        self,
        id: int,
        current_user: User,
        is_executive: bool,
    ) -> None:
        pig = self.get_by_id(id)

        if not is_executive and pig.owner != current_user.id:
            raise HTTPException(403, detail="타인의 시그/피그를 삭제할 수 없습니다")

        if pig.status == SCSCStatus.inactive:
            raise HTTPException(400, detail="해당 시그/피그는 이미 비활성 상태입니다")

        pig.status = SCSCStatus.inactive
        self.pig_repository.update(pig)

        await send_discord_bot_request_no_reply(
            action_code=4004,
            body={
                "pig_name": pig.title,
                "previous_semester": f"{pig.year}-{map_semester_name.get(pig.semester)}",
            },
        )

        logger.info(
            f"info_type=pig_deleted ; pig_id={pig.id} ; remover_id={current_user.id}"
        )

    def _handover_pig_ctrl(
        self, pig: PIG, new_owner_id: str, executor_id: str, is_forced: bool
    ) -> PIG:
        if pig.owner == new_owner_id:
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

        member = self.pig_member_repository.get_by_pig_and_user_id(pig.id, new_owner_id)
        if member is None:
            raise HTTPException(
                status_code=404,
                detail="새로운 시그/피그장은 해당 시그/피그의 구성원이어야 합니다",
            )

        old_owner = pig.owner
        pig.owner = new_owner_id
        self.pig_repository.update(pig)

        handover_type = "forced" if is_forced else "voluntary"
        logger.info(
            f"info_type=pig_handover ; handover_type={handover_type} ; pig_id={pig.id} ; title={pig.title} ; "
            f"executor_id={executor_id} ; old_owner_id={old_owner} ; new_owner_id={new_owner_id} ; "
            f"year={pig.year} ; semester={pig.semester}"
        )

        return pig

    def handover_pig(
        self,
        id: int,
        current_user: User,
        body: BodyHandoverPIG,
        is_executive: bool,
    ):
        pig = self.get_by_id(id)
        if not is_executive and current_user.id != pig.owner:
            raise HTTPException(403, detail="타인의 시그/피그를 변경할 수 없습니다")
        self._handover_pig_ctrl(pig, body.new_owner, current_user.id, is_executive)

    def get_members(self, id: int) -> Sequence[PigMemberResponse]:
        self.get_by_id(id)

        members = self.pig_member_repository.get_members_by_pig_id(id)
        res: list[PigMemberResponse] = []
        for member in members:
            user = self.user_repository.get_by_id(member.user_id)

            user_response = None
            if user:
                user_response = UserResponse.model_validate(user)

            member_response = PigMemberResponse(
                id=member.id,
                ig_id=member.ig_id,
                user_id=member.user_id,
                created_at=member.created_at,
                user=user_response,
            )
            res.append(member_response)

        return res

    async def join_pig(self, id: int, current_user: User) -> None:
        pig = self.get_by_id(id)
        allowed = (
            ctrl_status_available.join_sigpig_rolling_admission
            if pig.is_rolling_admission
            else ctrl_status_available.join_sigpig
        )
        if pig.status not in allowed:
            raise HTTPException(
                400, f"시그/피그 상태가 {allowed}일 때만 시그/피그에 가입할 수 있습니다"
            )

        pig_member = PIGMember(ig_id=id, user_id=current_user.id)
        try:
            self.pig_member_repository.create(pig_member)
        except IntegrityError:
            raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")

        if current_user.discord_id:
            await send_discord_bot_request_no_reply(
                action_code=2001,
                body={"user_id": current_user.discord_id, "role_name": pig.title},
            )

        logger.info(
            f"info_type=pig_join ; pig_id={pig.id} ; title={pig.title} ; executor_id={current_user.id} ; joined_user_id={current_user.id} ; year={pig.year} ; semester={pig.semester}"
        )

    async def executive_join_pig(
        self,
        id: int,
        current_user: User,
        body: BodyExecutiveJoinPIG,
    ) -> None:
        pig = self.get_by_id(id)
        user = self.user_repository.get_by_id(body.user_id)
        if not user:
            raise HTTPException(404, detail="해당 id의 사용자가 없습니다")

        pig_member = PIGMember(ig_id=id, user_id=body.user_id)
        try:
            self.pig_member_repository.create(pig_member)
        except IntegrityError:
            raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")

        if user.discord_id:
            await send_discord_bot_request_no_reply(
                action_code=2001,
                body={"user_id": user.discord_id, "role_name": pig.title},
            )

        logger.info(
            f"info_type=pig_join ; pig_id={pig.id} ; title={pig.title} ; executor_id={current_user.id} ; joined_user_id={body.user_id} ; year={pig.year} ; semester={pig.semester}"
        )

    async def leave_pig(self, id: int, current_user: User) -> None:
        pig = self.get_by_id(id)
        allowed = (
            ctrl_status_available.join_sigpig_rolling_admission
            if pig.is_rolling_admission
            else ctrl_status_available.join_sigpig
        )
        if pig.status not in allowed:
            raise HTTPException(
                400,
                f"시그/피그 상태가 {allowed}일 때만 시그/피그에서 탈퇴할 수 있습니다",
            )
        if pig.owner == current_user.id:
            raise HTTPException(
                409, detail="시그/피그장은 해당 시그/피그를 탈퇴할 수 없습니다"
            )

        member = self.pig_member_repository.get_by_pig_and_user_id(id, current_user.id)
        if not member:
            raise HTTPException(404, detail="시그/피그의 구성원이 아닙니다")

        self.pig_member_repository.delete(member)

        if current_user.discord_id:
            await send_discord_bot_request_no_reply(
                action_code=2002,
                body={"user_id": current_user.discord_id, "role_name": pig.title},
            )

        logger.info(
            f"info_type=pig_leave ; pig_id={pig.id} ; title={pig.title} ; executor_id={current_user.id} ; left_user_id={current_user.id} ; year={pig.year} ; semester={pig.semester}"
        )

    async def executive_leave_pig(
        self,
        id: int,
        current_user: User,
        body: BodyExecutiveLeavePIG,
    ) -> None:
        pig = self.get_by_id(id)
        user = self.user_repository.get_by_id(body.user_id)
        if not user:
            raise HTTPException(404, detail="해당 id의 사용자가 없습니다")

        if pig.owner == user.id:
            raise HTTPException(
                409, detail="시그/피그장은 해당 시그/피그를 탈퇴할 수 없습니다"
            )

        member = self.pig_member_repository.get_by_pig_and_user_id(id, body.user_id)
        if not member:
            raise HTTPException(404, detail="시그/피그의 구성원이 아닙니다")

        self.pig_member_repository.delete(member)

        if user.discord_id:
            await send_discord_bot_request_no_reply(
                action_code=2002,
                body={"user_id": user.discord_id, "role_name": pig.title},
            )

        logger.info(
            f"info_type=pig_leave ; pig_id={pig.id} ; title={pig.title} ; executor_id={current_user.id} ; left_user_id={body.user_id} ; year={pig.year} ; semester={pig.semester}"
        )


PigServiceDep = Annotated[PigService, Depends()]
