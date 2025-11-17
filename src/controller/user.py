import asyncio
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional, Sequence

import jwt
from fastapi import Depends, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.core import get_settings, logger
from src.db import SessionDep
from src.model import OldboyApplicant, StandbyReqTbl, User, UserResponse, UserStatus
from src.util import (
    DepositDTO,
    change_discord_role,
    generate_user_hash,
    get_user_role_level,
    is_valid_img_url,
    is_valid_phone,
    is_valid_student_id,
    process_standby_user,
    sha256_hash,
    validate_and_read_file,
)


class BodyCreateUser(BaseModel):
    email: str
    name: str
    phone: str
    student_id: str
    major_id: int
    profile_picture: str
    profile_picture_is_url: bool
    hashToken: str


class BodyLogin(BaseModel):
    email: str
    hashToken: str


class ResponseLogin(BaseModel):
    jwt: str


class BodyUpdateUser(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    student_id: Optional[str] = None
    major_id: Optional[int] = None
    role: Optional[str] = None
    status: Optional[UserStatus] = None
    discord_id: Optional[int] = None
    discord_name: Optional[str] = None


class BodyUpdateMyProfile(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    student_id: Optional[str] = None
    major_id: Optional[int] = None
    profile_picture: Optional[str] = None
    profile_picture_is_url: Optional[bool] = None


class ProcessStandbyListManuallyBody(BaseModel):
    id: str


class ProcessDepositResult(BaseModel):
    result_code: int
    result_msg: str
    record: DepositDTO
    users: list[UserResponse]


class ProcessStandbyListResponse(BaseModel):
    cnt_succeeded_records: int
    cnt_failed_records: int
    results: list[ProcessDepositResult]

    model_config = {"from_attributes": True}  # enables reading from ORM objects


class ProcessDepositResponse(BaseModel):
    result: ProcessDepositResult

    model_config = {"from_attributes": True}  # enables reading from ORM objects


async def create_user_ctrl(session: SessionDep, body: BodyCreateUser) -> User:
    if not is_valid_phone(body.phone):
        raise HTTPException(422, detail="invalid phone number")
    if not is_valid_student_id(body.student_id):
        raise HTTPException(422, detail="invalid student_id")
    valid = await asyncio.to_thread(is_valid_img_url, body.profile_picture)
    if body.profile_picture_is_url and not valid:
        raise HTTPException(400, detail="invalid image url")

    expected = generate_user_hash(body.email)
    if not hmac.compare_digest(body.hashToken, expected):
        raise HTTPException(401, detail="invalid hash token")

    user = User(
        id=sha256_hash(body.email.lower()),
        email=body.email,
        name=body.name,
        phone=body.phone,
        student_id=body.student_id,
        role=get_user_role_level("newcomer"),
        major_id=body.major_id,
        profile_picture=body.profile_picture,
        profile_picture_is_url=body.profile_picture_is_url,
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="unique field already exists")
    session.refresh(user)
    logger.info(f"info_type=user_created ; user_id={user.id}")
    return user


def enroll_user_ctrl(session: SessionDep, user_id: str) -> StandbyReqTbl:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, detail="user not found")
    if user.status != UserStatus.pending:
        raise HTTPException(400, detail="Only user with pending status can enroll")
    user.status = UserStatus.standby
    session.add(user)
    stby_req_tbl = StandbyReqTbl(
        standby_user_id=user.id,
        user_name=user.name,
        deposit_name=f"{user.name}{user.phone[-2:]}",
        is_checked=False,
    )
    session.add(stby_req_tbl)
    session.commit()
    session.refresh(stby_req_tbl)
    logger.info(f"info_type=user_enrolled ; user_id={user_id}")
    return stby_req_tbl


def verify_enroll_user_ctrl(
    session: SessionDep, user: User, stby_req: StandbyReqTbl, deposit: DepositDTO
) -> None:
    user.status = UserStatus.active
    stby_req.deposit_time = deposit.deposit_time
    stby_req.deposit_name = deposit.deposit_name
    stby_req.is_checked = True
    session.add(user)
    session.add(stby_req)
    session.commit()
    return


async def process_deposit_ctrl(
    session: SessionDep, deposit: DepositDTO
) -> ProcessDepositResult:
    try:
        query_standbyreq = select(StandbyReqTbl).where(
            StandbyReqTbl.is_checked == False
        )
        if deposit.deposit_name[-2:].isdigit():
            query_standbyreq = query_standbyreq.where(
                StandbyReqTbl.deposit_name == deposit.deposit_name
            )  # search on deposit_name, which is "name+last 2 phone number" form
        else:
            query_standbyreq = query_standbyreq.where(
                StandbyReqTbl.user_name == deposit.deposit_name
            )  # search on user_name, which is "name" form
        matching_standbyreqs = session.exec(query_standbyreq).all()
        matching_users = [
            UserResponse.model_validate(session.get(User, u.standby_user_id))
            for u in matching_standbyreqs
        ]

        if len(matching_standbyreqs) > 1:  # multiple standby request found
            logger.error(
                f"err_type=deposit ; err_code=409 ; msg={len(matching_standbyreqs)}users match the following deposit record ; deposit={deposit} ; users={matching_users}"
            )
            return ProcessDepositResult(
                result_code=409,
                result_msg=f"해당 입금 기록에 대응하는 사용자가 입금 대기자 명단에 {len(matching_standbyreqs)}건 존재합니다",
                record=deposit,
                users=matching_users,
            )

        if len(matching_standbyreqs) == 0:
            query_matching_users_error = select(User)
            if deposit.deposit_name[-2:].isdigit():
                query_matching_users_error = query_matching_users_error.where(
                    User.name == deposit.deposit_name[:-2],
                    func.substring(User.phone, func.length(User.phone) - 1, 2)
                    == deposit.deposit_name[-2:],
                )
            else:
                query_matching_users_error = query_matching_users_error.where(
                    User.name == deposit.deposit_name
                )
            matching_users_error = session.exec(query_matching_users_error).all()
            matching_users = [
                UserResponse.model_validate(u) for u in matching_users_error
            ]

            if len(matching_users_error) != 1:
                if len(matching_users_error) > 1:
                    logger.error(
                        f"err_type=deposit ; err_code=409 ; msg={len(matching_users_error)}users match the following deposit record ; deposit={deposit} ; users={matching_users}"
                    )
                    return ProcessDepositResult(
                        result_code=409,
                        result_msg=f"해당 입금 기록에 대응하는 사용자가 사용자 테이블에 {len(matching_users_error)}건 존재합니다",
                        record=deposit,
                        users=matching_users,
                    )

                # else
                logger.error(
                    f"err_type=deposit ; err_code=404 ; msg=no users match the following deposit record ; deposit={deposit} ; users={matching_users}"
                )
                return ProcessDepositResult(
                    result_code=404,
                    result_msg="해당 입금 기록에 대응하는 사용자가 사용자 테이블에 존재하지 않습니다",
                    record=deposit,
                    users=matching_users,
                )

            user = matching_users_error[0]
            if user.status != UserStatus.pending:
                logger.error(
                    f"err_type=deposit ; err_code=412 ; msg=user is not in pending status but in {user.status} status ; deposit={deposit} ; users={matching_users}"
                )
                return ProcessDepositResult(
                    result_code=412,
                    result_msg=f"해당 입금 기록에 대응하는 사용자의 상태는 {user.status}로 pending 상태가 아닙니다",
                    record=deposit,
                    users=matching_users,
                )
            matching_standbyreqs = [enroll_user_ctrl(session, user.id)]

        # len(matching_standbyreqs) == 1:
        if deposit.amount < get_settings().enrollment_fee:
            logger.error(
                f"err_type=deposit ; err_code=402 ; msg=deposit amount is less than the required {get_settings().enrollment_fee} won ; deposit={deposit} ; users={matching_users}"
            )
            return ProcessDepositResult(
                result_code=402,
                result_msg=f"입금액이 {get_settings().enrollment_fee}원보다 적습니다",
                record=deposit,
                users=matching_users,
            )
        if deposit.amount > get_settings().enrollment_fee:
            logger.error(
                f"err_type=deposit ; err_code=413 ; msg=deposit amount is more than the required {get_settings().enrollment_fee} won ; deposit={deposit} ; users={matching_users}"
            )
            return ProcessDepositResult(
                result_code=413,
                result_msg=f"입금액이 {get_settings().enrollment_fee}원보다 많습니다",
                record=deposit,
                users=matching_users,
            )

        stby_user = matching_standbyreqs[0]
        user = session.get(User, stby_user.standby_user_id)
        if not user:
            logger.error(
                f"err_type=deposit ; err_code=500 ; msg=unexpected error: user not found in user table ; deposit={deposit} ; users={matching_users}"
            )
            return ProcessDepositResult(
                result_code=500,
                result_msg="알 수 없는 오류: user not found in user table",
                record=deposit,
                users=matching_users,
            )
        if user.status != UserStatus.standby:
            logger.error(
                f"err_type=deposit ; err_code=412 ; msg=user is not in standby status but in {user.status} status ; deposit={deposit} ; users={matching_users}"
            )
            return ProcessDepositResult(
                result_code=412,
                result_msg=f"해당 입금 기록에 대응하는 사용자의 상태는 {user.status}로 standby 상태가 아닙니다",
                record=deposit,
                users=matching_users,
            )
        verify_enroll_user_ctrl(session, user, stby_user, deposit)
        logger.info(f"info_type=deposit ; deposit={deposit} ; users={matching_users}")
        return ProcessDepositResult(
            result_code=200, result_msg="성공", record=deposit, users=matching_users
        )
    except Exception as e:
        logger.error(
            f"err_type=deposit ; err_code=500 ; msg=unexpected error: {e} ; deposit={deposit}"
        )
        return ProcessDepositResult(
            result_code=500,
            result_msg=f"알 수 없는 오류: {e}",
            record=deposit,
            users=[],
        )


async def register_oldboy_applicant_ctrl(
    session: SessionDep, user: User
) -> OldboyApplicant:
    user_created_at_aware = user.created_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - user_created_at_aware < timedelta(weeks=52 * 3):
        raise HTTPException(400, detail="must have been a member for at least 3 years.")
    if user.role != get_user_role_level("member"):
        raise HTTPException(400, detail="must be a member")
    oldboy_applicant = OldboyApplicant(id=user.id)
    session.add(oldboy_applicant)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="oldboy_applicant already exists")
    session.refresh(oldboy_applicant)
    return oldboy_applicant


async def process_oldboy_applicant_ctrl(session: SessionDep, user_id: str) -> None:
    oldboy_applicant = session.get(OldboyApplicant, user_id)
    if not oldboy_applicant:
        raise HTTPException(404, detail="oldboy_applicant not found")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(503, detail="user does not exist")
    if user.role == get_user_role_level("oldboy"):
        raise HTTPException(409, detail="user is already oldboy")

    oldboy_applicant.processed = True
    session.add(oldboy_applicant)
    user.role = get_user_role_level("oldboy")
    session.add(user)
    session.commit()
    if user.discord_id:
        await change_discord_role(session, user.discord_id, "oldboy")
    return


async def reactivate_oldboy_ctrl(session: SessionDep, user: User) -> None:
    if user.role != get_user_role_level("oldboy"):
        raise HTTPException(400, detail="you are not oldboy")

    user.role = get_user_role_level("member")
    user.status = UserStatus.pending
    session.add(user)

    oldboy_applicant = session.get(OldboyApplicant, user.id)
    if oldboy_applicant:
        session.delete(oldboy_applicant)

    if user.discord_id:
        await change_discord_role(session, user.discord_id, "member")
    session.commit()
    return


class UserService:
    def __init__(self, session: SessionDep):
        self.session = session

    async def create_user(self, body):
        return await create_user_ctrl(self.session, body)

    async def enroll_user(self, user_id: str):
        enroll_user_ctrl(self.session, user_id)

    def get_user_by_id(self, id: str) -> UserResponse:
        user = self.session.get(User, id)
        if not user:
            raise HTTPException(404, detail="user not found")
        return UserResponse.model_validate(user)

    def get_users(
        self,
        email: Optional[str] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        student_id: Optional[str] = None,
        user_role: Optional[str] = None,
        status: Optional[str] = None,
        discord_id: Optional[str] = None,
        discord_name: Optional[str] = None,
        major_id: Optional[int] = None,
    ) -> Sequence[User]:
        query = select(User)
        if email:
            query = query.where(User.email == email)
        if name:
            query = query.where(User.name == name)
        if phone:
            query = query.where(User.phone == phone)
        if student_id:
            query = query.where(User.student_id == student_id)
        if user_role:
            query = query.where(User.role == get_user_role_level(user_role))
        if status:
            query = query.where(User.status == status)
        if discord_id is not None:
            if discord_id == "":
                query = query.where(User.discord_id == None)
            else:
                try:
                    query = query.where(User.discord_id == int(discord_id))
                except ValueError:
                    raise HTTPException(
                        422,
                        detail=[
                            {
                                "type": "int_parsing",
                                "loc": ["query", "discord_id"],
                                "msg": "Input should be a valid integer, unable to parse string as an integer",
                                "input": discord_id,
                            }
                        ],
                    )
        if discord_name is not None:
            if discord_name == "":
                query = query.where(User.discord_name == None)
            else:
                query = query.where(User.discord_name == discord_name)
        if major_id:
            query = query.where(User.major_id == major_id)
        return self.session.exec(query).all()

    @staticmethod
    def get_role_names(lang: str | None = "en"):
        if lang == "ko":
            return {
                "role_names": {
                    "0": "최저권한",
                    "100": "휴회원",
                    "200": "준회원",
                    "300": "정회원",
                    "400": "졸업생",
                    "500": "운영진",
                    "1000": "회장",
                }
            }
        return {
            "role_names": {
                "0": "lowest",
                "100": "dormant",
                "200": "newcomer",
                "300": "member",
                "400": "oldboy",
                "500": "executive",
                "1000": "president",
            }
        }

    async def update_my_profile(self, current_user, body: BodyUpdateMyProfile):
        if body.phone and not is_valid_phone(body.phone):
            raise HTTPException(422, detail="invalid phone number")
        if body.student_id and not is_valid_student_id(body.student_id):
            raise HTTPException(422, detail="invalid student_id")
        if body.name:
            current_user.name = body.name
        if body.phone:
            current_user.phone = body.phone
        if body.student_id:
            current_user.student_id = body.student_id
        if body.major_id is not None:
            current_user.major_id = body.major_id
        if body.profile_picture:
            if not is_valid_img_url(body.profile_picture):
                raise HTTPException(400, detail="invalid image url")
            current_user.profile_picture = body.profile_picture
        if body.profile_picture_is_url is not None:
            current_user.profile_picture_is_url = body.profile_picture_is_url
        self.session.add(current_user)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise HTTPException(409, detail="unique field already exists")
        return

    async def update_my_pfp_file(self, current_user, file: UploadFile):
        content, _, ext, _ = await validate_and_read_file(
            file, valid_mime_type="image/", valid_ext=frozenset({"png", "jpg", "jpeg"})
        )

        filename = f"{current_user.id}.{ext}"
        path = f"static/image/pfps/{filename}"
        with open(path, "wb") as fp:
            fp.write(content)
        current_user.profile_picture = path
        current_user.profile_picture_is_url = False
        self.session.add(current_user)
        try:
            self.session.commit()
        except IntegrityError as err:
            self.session.rollback()
            try:
                os.remove(path)
            except OSError:
                logger.warning(
                    "warn_type=pfp_upload_cleanup_failed ; %s", path, exc_info=True
                )
            raise HTTPException(409, detail="unique field already exists") from err

    async def delete_my_profile(self, current_user):
        if current_user.role >= get_user_role_level("executive"):
            raise HTTPException(
                403,
                detail="임원진 이상의 권한은 휴회원으로 전환할 수 없습니다.",
            )
        current_user.role = get_user_role_level("dormant")
        self.session.add(current_user)
        self.session.commit()
        self.session.refresh(current_user)
        if current_user.discord_id:
            await change_discord_role(self.session, current_user.discord_id, "dormant")

    async def login(self, body):
        expected = generate_user_hash(body.email)
        if not hmac.compare_digest(body.hashToken, expected):
            raise HTTPException(401, detail="invalid hash token")

        result = self.session.get(User, sha256_hash(body.email.lower()))
        if result is None:
            raise HTTPException(404, detail="invalid email address")
        result.last_login = datetime.now(timezone.utc)
        self.session.add(result)
        self.session.commit()

        payload = {
            "user_id": result.id,
            "exp": datetime.now(timezone.utc)
            + timedelta(seconds=get_settings().jwt_valid_seconds),
        }
        encoded_jwt = jwt.encode(payload, get_settings().jwt_secret, "HS256")
        return ResponseLogin(jwt=encoded_jwt)

    async def update_user(self, current_user, id: str, body: BodyUpdateUser):
        user = self.session.get(User, id)
        if user is None:
            raise HTTPException(404, detail="no user exists")
        old_role = user.role

        if (current_user.role <= user.role) and not (
            current_user.role == user.role == 1000
        ):
            raise HTTPException(
                403,
                detail=f"Cannot update user with a higher or equal role than yourself, current role: {current_user.role}, {user.email}, user role: {user.role}",
            )
        if body.role:
            level = get_user_role_level(body.role)
            if current_user.role < level:
                raise HTTPException(403, detail="Cannot assign role higher than yours")
            user.role = level

        if body.phone:
            if not is_valid_phone(body.phone):
                raise HTTPException(422, detail="invalid phone number")
            user.phone = body.phone
        if body.student_id:
            if not is_valid_student_id(body.student_id):
                raise HTTPException(422, detail="invalid student_id")
            user.student_id = body.student_id

        if body.name:
            user.name = body.name
        if body.major_id:
            user.major_id = body.major_id
        if body.status:
            user.status = body.status
        if body.discord_id:
            user.discord_id = body.discord_id
        if body.discord_name:
            user.discord_name = body.discord_name

        self.session.add(user)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise HTTPException(409, detail="unique field already exists")
        if body.role:
            self.session.refresh(user)
            logger.info(
                f"info_type=user_role_updated ; user_id={id} ; old_role={old_role} ; new_role={get_user_role_level(body.role)} ; executor={current_user.id}"
            )
            if user.discord_id:
                await change_discord_role(self.session, user.discord_id, body.role)


class OldboyService:
    def __init__(self, session: SessionDep):
        self.session = session

    async def register_applicant(self, current_user):
        return await register_oldboy_applicant_ctrl(self.session, current_user)

    def get_applicant_self(self, user_id: str) -> OldboyApplicant:
        applicant = self.session.get(OldboyApplicant, user_id)
        if applicant is None:
            raise HTTPException(404, detail="applicant not found for user")
        return applicant

    def get_all_applicants(self):
        return self.session.exec(select(OldboyApplicant)).all()

    async def process_applicant(self, id: str):
        await process_oldboy_applicant_ctrl(self.session, id)

    async def delete_applicant_self(self, user_id: str):
        oldboy_applicant = self.session.get(OldboyApplicant, user_id)
        if not oldboy_applicant:
            raise HTTPException(404, detail="oldboy_applicant not found")
        if oldboy_applicant.processed:
            raise HTTPException(409, detail="oldboy_applicant already processed")
        self.session.delete(oldboy_applicant)
        self.session.commit()

    async def delete_applicant_executive(self, id: str):
        user = self.session.get(User, id)
        if not user:
            raise HTTPException(404, detail="user does not exist")
        oldboy_applicant = self.session.get(OldboyApplicant, user.id)
        if not oldboy_applicant:
            raise HTTPException(404, detail="oldboy_applicant not found")
        self.session.delete(oldboy_applicant)
        self.session.commit()

    async def reactivate(self, current_user):
        await reactivate_oldboy_ctrl(self.session, current_user)


class StandbyService:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_standby_list(self):
        return self.session.exec(select(StandbyReqTbl)).all()

    async def process_standby_list_manually(
        self, current_user, body: ProcessStandbyListManuallyBody
    ):
        user = self.session.get(User, body.id)
        if not user:
            raise HTTPException(404, detail="user not found")
        if user.status == UserStatus.active:
            raise HTTPException(409, detail="the user is already active")
        user.status = UserStatus.active
        self.session.add(user)
        standbyreq = self.session.exec(
            select(StandbyReqTbl)
            .where(StandbyReqTbl.standby_user_id == body.id)
            .where(StandbyReqTbl.is_checked == False)
        ).first()
        if standbyreq:
            standbyreq.is_checked = True
            standbyreq.deposit_name = f"Manually by {current_user.name}"
            standbyreq.deposit_time = datetime.now(timezone.utc)
        else:
            standbyreq = StandbyReqTbl(
                standby_user_id=user.id,
                user_name=user.name,
                deposit_name=f"Manually by {current_user.name}",
                deposit_time=datetime.now(timezone.utc),
                is_checked=True,
            )
        self.session.add(standbyreq)
        self.session.commit()

    async def process_standby_list(
        self, file: UploadFile
    ) -> ProcessStandbyListResponse:
        content, _, _, _ = await validate_and_read_file(
            file, valid_ext=frozenset({"csv"})
        )
        try:
            deposit_array = await process_standby_user("utf-8", content)
        except UnicodeDecodeError:
            try:
                deposit_array = await process_standby_user("euc-kr", content)
            except UnicodeDecodeError:
                raise HTTPException(
                    400,
                    detail="파일 읽기 실패: utf-8, euc-kr 인코딩만 읽을 수 있습니다",
                )
            except Exception as e:
                raise HTTPException(400, detail=f"파일 읽기 실패: {e}")
        except Exception as e:
            raise HTTPException(400, detail=f"파일 읽기 실패: {e}")

        cnt_succeeded_records = 0
        cnt_failed_records = 0
        results: list[ProcessDepositResult] = []
        for deposit in deposit_array:
            result = await process_deposit_ctrl(self.session, deposit)
            if result.result_code == 200:
                cnt_succeeded_records += 1
            else:
                cnt_failed_records += 1
            results.append(result)

        return ProcessStandbyListResponse(
            cnt_succeeded_records=cnt_succeeded_records,
            cnt_failed_records=cnt_failed_records,
            results=results,
        )

    async def process_deposit(self, body: DepositDTO) -> ProcessDepositResponse:
        result = await process_deposit_ctrl(self.session, body)
        return ProcessDepositResponse(result=result)


UserServiceDep = Annotated[UserService, Depends()]
StandbyServiceDep = Annotated[StandbyService, Depends()]
OldboyServiceDep = Annotated[OldboyService, Depends()]
