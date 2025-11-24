from typing import Annotated, Optional, Sequence

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.core import logger
from src.db import SessionDep
from src.model import SIG, SCSCGlobalStatus, SCSCStatus, SIGMember, User
from src.util import (
    get_user_role_level,
    map_semester_name,
    send_discord_bot_request_no_reply,
)

from .article import BodyCreateArticle, create_article_ctrl
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


async def create_sig_ctrl(
    session: SessionDep,
    body: BodyCreateSIG,
    user_id: str,
    user_discord_id: Optional[int],
    scsc_global_status: SCSCGlobalStatus,
) -> SIG:
    if scsc_global_status.status not in ctrl_status_available.create_sigpig:
        raise HTTPException(
            400,
            f"SCSC 전역 상태가 {ctrl_status_available.create_sigpig}일 때만 시그/피그를 생성할 수 있습니다",
        )

    sig_article = await create_article_ctrl(
        session,
        BodyCreateArticle(title=body.title, content=body.content, board_id=1),
        user_id,
        get_user_role_level("president"),
    )

    sig = SIG(
        title=body.title,
        description=body.description,
        content_id=sig_article.id,
        year=scsc_global_status.year,
        semester=scsc_global_status.semester,
        owner=user_id,
        status=scsc_global_status.status,
        is_rolling_admission=body.is_rolling_admission,
    )
    session.add(sig)
    try:
        session.flush()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")
    session.refresh(sig)

    if sig.id is None:
        raise HTTPException(503, detail="sig primary key does not exist")
    sig_member = SIGMember(ig_id=sig.id, user_id=user_id)
    session.add(sig_member)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="시그장 자동 가입 중 중복 오류가 발생했습니다")
    session.refresh(sig)
    if user_discord_id:
        await send_discord_bot_request_no_reply(
            action_code=4003,
            body={
                "sig_name": sig.title,
                "user_id_list": [user_discord_id],
                "sig_description": sig.description,
            },
        )
    logger.info(
        f"info_type=sig_created ; sig_id={sig.id} ; title={sig.title} ; owner_id={user_id} ; year={sig.year} ; semester={sig.semester} ; is_rolling_admission={sig.is_rolling_admission}"
    )
    return sig


async def update_sig_ctrl(
    session: SessionDep, id: int, body: BodyUpdateSIG, user_id: str, is_executive: bool
) -> None:
    sig = session.get(SIG, id)
    if not sig:
        raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
    if not is_executive and sig.owner != user_id:
        raise HTTPException(
            status_code=403, detail="타인의 시그/피그를 변경할 수 없습니다"
        )
    old_title = sig.title
    if body.title:
        sig.title = body.title
    if body.description:
        sig.description = body.description
    if body.content:
        sig_article = await create_article_ctrl(
            session,
            BodyCreateArticle(title=sig.title, content=body.content, board_id=1),
            user_id,
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

    session.add(sig)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")
    session.refresh(sig)

    bot_body = {}
    bot_body["sig_name"] = old_title
    if body.title:
        bot_body["new_sig_name"] = body.title
    if body.description:
        bot_body["new_topic"] = body.description
    if len(bot_body) > 1:
        await send_discord_bot_request_no_reply(action_code=4006, body=bot_body)

    logger.info(
        f"info_type=sig_updated ; sig_id={id} ; title={sig.title} ; revisioner_id={user_id} ; year={sig.year} ; semester={sig.semester} ; is_rolling_admission={sig.is_rolling_admission}"
    )
    return


def handover_sig_ctrl(
    session: SessionDep, sig: SIG, new_owner_id: str, executor_id: str, is_forced: bool
) -> SIG:
    if sig.owner == new_owner_id:
        raise HTTPException(
            status_code=400,
            detail="새로운 시그/피그장은 현재 시그/피그장과 달라야 합니다",
        )

    new_owner_user = session.get(User, new_owner_id)
    if not new_owner_user:
        raise HTTPException(
            status_code=404, detail="새로운 시그/피그장에 해당하는 사용자가 없습니다"
        )

    member = session.exec(
        select(SIGMember)
        .where(SIGMember.ig_id == sig.id)
        .where(SIGMember.user_id == new_owner_id)
    ).first()
    if not member:
        raise HTTPException(
            status_code=404,
            detail="새로운 시그/피그장은 해당 시그/피그의 구성원이어야 합니다",
        )

    old_owner = sig.owner
    sig.owner = new_owner_id
    session.add(sig)
    session.commit()
    session.refresh(sig)

    handover_type = "forced" if is_forced else "voluntary"
    logger.info(
        f"info_type=sig_handover ; handover_type={handover_type} ; sig_id={sig.id} ; title={sig.title} ; "
        f"executor_id={executor_id} ; old_owner_id={old_owner} ; new_owner_id={new_owner_id} ; "
        f"year={sig.year} ; semester={sig.semester}"
    )

    return sig


class SigService:
    def __init__(
        self,
        session: SessionDep,
    ):
        self.session = session

    async def create_sig(
        self,
        scsc_global_status: SCSCGlobalStatus,
        current_user: User,
        body: BodyCreateSIG,
    ):
        return await create_sig_ctrl(
            self.session,
            body,
            current_user.id,
            current_user.discord_id,
            scsc_global_status,
        )

    def get_by_id(self, id: int) -> SIG:
        sig = self.session.get(SIG, id)
        if not sig:
            raise HTTPException(404, detail="해당 id의 시그/피그가 없습니다")
        return sig

    def get_all(self) -> Sequence[SIG]:
        return self.session.exec(select(SIG)).all()

    async def update_sig(
        self,
        id: int,
        current_user: User,
        body: BodyUpdateSIG,
        is_executive: bool,
    ):
        await update_sig_ctrl(self.session, id, body, current_user.id, is_executive)

    async def delete_sig(
        self,
        id: int,
        current_user: User,
        is_executive: bool,
    ):
        sig = self.get_by_id(id)
        if not is_executive and sig.owner != current_user.id:
            raise HTTPException(403, detail="타인의 시그/피그를 삭제할 수 없습니다")
        if sig.status == SCSCStatus.inactive:
            raise HTTPException(400, detail="해당 시그/피그는 이미 비활성 상태입니다")

        sig.status = SCSCStatus.inactive
        self.session.commit()
        self.session.refresh(sig)

        await send_discord_bot_request_no_reply(
            action_code=4004,
            body={
                "sig_name": sig.title,
                "previous_semester": f"{sig.year}-{map_semester_name.get(sig.semester)}",
            },
        )

        logger.info(
            f"info_type=sig_deleted ; sig_id={sig.id} ; remover_id={current_user.id}"
        )

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
        handover_sig_ctrl(
            self.session, sig, body.new_owner, current_user.id, is_executive
        )

    def get_members(self, id: int):
        res = []
        for member in self.session.exec(
            select(SIGMember).where(SIGMember.ig_id == id)
        ).all():
            user = self.session.get(User, member.user_id)
            member_dict = member.model_dump()
            member_dict["user"] = user.model_dump() if user else {}
            res.append(member_dict)
        return res

    async def join_sig(self, id: int, current_user: User):
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
        self.session.add(sig_member)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")
        self.session.refresh(sig)
        if current_user.discord_id:
            await send_discord_bot_request_no_reply(
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
    ):
        sig = self.get_by_id(id)
        user = self.session.get(User, body.user_id)
        if not user:
            raise HTTPException(404, detail="해당 id의 사용자가 없습니다")
        sig_member = SIGMember(ig_id=id, user_id=body.user_id)
        self.session.add(sig_member)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise HTTPException(409, detail="기존 시그/피그와 중복된 항목이 있습니다")
        self.session.refresh(user)
        self.session.refresh(sig)
        if user.discord_id:
            await send_discord_bot_request_no_reply(
                action_code=2001,
                body={"user_id": user.discord_id, "role_name": sig.title},
            )
        logger.info(
            f"info_type=sig_join ; sig_id={sig.id} ; title={sig.title} ; executor_id={current_user.id} ; joined_user_id={body.user_id} ; year={sig.year} ; semester={sig.semester}"
        )
        return

    async def leave_sig(self, id: int, current_user: User):
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
        sig_members = self.session.exec(
            select(SIGMember)
            .where(SIGMember.ig_id == id)
            .where(SIGMember.user_id == current_user.id)
        ).all()
        if not sig_members:
            raise HTTPException(404, detail="시그/피그의 구성원이 아닙니다")

        for member in sig_members:
            self.session.delete(member)

        self.session.commit()
        self.session.refresh(sig)
        if current_user.discord_id:
            await send_discord_bot_request_no_reply(
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
    ):
        sig = self.get_by_id(id)
        user = self.session.get(User, body.user_id)
        if not user:
            raise HTTPException(404, detail="해당 id의 사용자가 없습니다")
        if sig.owner == user.id:
            raise HTTPException(
                409, detail="시그/피그장은 해당 시그/피그를 탈퇴할 수 없습니다"
            )
        sig_members = self.session.exec(
            select(SIGMember)
            .where(SIGMember.ig_id == id)
            .where(SIGMember.user_id == body.user_id)
        ).all()
        if not sig_members:
            raise HTTPException(404, detail="시그/피그의 구성원이 아닙니다")
        for member in sig_members:
            self.session.delete(member)
        self.session.commit()
        self.session.refresh(user)
        self.session.refresh(sig)
        if user.discord_id:
            await send_discord_bot_request_no_reply(
                action_code=2002,
                body={"user_id": user.discord_id, "role_name": sig.title},
            )
        logger.info(
            f"info_type=sig_leave ; sig_id={sig.id} ; title={sig.title} ; executor_id={current_user.id} ; left_user_id={body.user_id} ; year={sig.year} ; semester={sig.semester}"
        )
        return


SigServiceDep = Annotated[SigService, Depends()]
