import asyncio
import hmac
from datetime import timedelta
from typing import Annotated, Optional, Sequence

import aiofiles
import jwt
from aiofiles import os as aiofiles_os
from fastapi import Depends, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.amqp import mq_client
from src.core import get_settings, logger
from src.model import OldboyApplicant, StandbyReqTbl, User, UserStatus
from src.repositories import (
    OldboyApplicantRepositoryDep,
    StandbyReqTblRepositoryDep,
    UserRepositoryDep,
    UserRoleRepositoryDep,
    get_user_role_level,
)
from src.schemas import PublicUserResponse, UserResponse
from src.util import (
    DepositDTO,
    generate_user_hash,
    is_valid_img_url,
    is_valid_phone,
    is_valid_student_id,
    process_standby_user,
    sha256_hash,
    utcnow,
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


class UserService:
    def __init__(
        self,
        user_repository: UserRepositoryDep,
        user_role_repository: UserRoleRepositoryDep,
        standby_repository: StandbyReqTblRepositoryDep,
    ) -> None:
        self.user_repository = user_repository
        self.user_role_repository = user_role_repository
        self.standby_repository = standby_repository

    async def create_user(self, body: BodyCreateUser) -> UserResponse:
        if not is_valid_phone(body.phone):
            raise HTTPException(422, detail="invalid phone number")
        if not is_valid_student_id(body.student_id):
            raise HTTPException(422, detail="invalid student_id")

        if body.profile_picture_is_url:
            valid = await asyncio.to_thread(is_valid_img_url, body.profile_picture)
            if not valid:
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

        try:
            user = self.user_repository.create(user)
        except IntegrityError:
            raise HTTPException(status_code=409, detail="unique field already exists")

        logger.info(f"info_type=user_created ; user_id={user.id}")
        return UserResponse.model_validate(user)

    async def enroll_user(self, user_id: str) -> None:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(404, detail="user not found")

        if user.status not in (UserStatus.pending, UserStatus.standby):
            raise HTTPException(
                400, detail="Only user with pending or standby status can enroll"
            )

        if user.status == UserStatus.pending:
            user.status = UserStatus.standby
            self.user_repository.update(user)

        stby_req_tbl = StandbyReqTbl(
            standby_user_id=user.id,
            user_name=user.name,
            deposit_name=f"{user.name}{user.phone[-2:]}",
            is_checked=False,
        )
        self.standby_repository.create(stby_req_tbl)

        logger.info(f"info_type=user_enrolled ; user_id={user_id}")

    def get_user_by_id(self, id: str) -> UserResponse:
        user = self.user_repository.get_by_id(id)
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
    ) -> Sequence[UserResponse]:
        filters = {}
        if email:
            filters["email"] = email
        if name:
            filters["name"] = name
        if phone:
            filters["phone"] = phone
        if student_id:
            filters["student_id"] = student_id
        if user_role:
            filters["role"] = get_user_role_level(user_role)
        if status:
            filters["status"] = status
        if major_id:
            filters["major_id"] = major_id

        if discord_id is not None:
            if discord_id == "":
                filters["discord_id"] = "IS_NULL"
            else:
                try:
                    filters["discord_id"] = int(discord_id)
                except ValueError:
                    raise HTTPException(
                        422,
                        detail=[
                            {
                                "type": "int_parsing",
                                "loc": ["query", "discord_id"],
                                "msg": "Input should be a valid integer",
                                "input": discord_id,
                            }
                        ],
                    )

        if discord_name is not None:
            if discord_name == "":
                filters["discord_name"] = "IS_NULL"
            else:
                filters["discord_name"] = discord_name

        users = self.user_repository.get_by_filters(filters)
        return UserResponse.model_validate_list(users)

    def get_public_executives(self) -> Sequence[PublicUserResponse]:
        return PublicUserResponse.model_validate_list(
            self.user_repository.get_executives()
        )

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

    async def update_my_profile(
        self, current_user: User, body: BodyUpdateMyProfile
    ) -> None:
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
            if body.profile_picture_is_url:
                valid = await asyncio.to_thread(is_valid_img_url, body.profile_picture)
                if not valid:
                    raise HTTPException(400, detail="invalid image url")
            current_user.profile_picture = body.profile_picture

        if body.profile_picture_is_url is not None:
            current_user.profile_picture_is_url = body.profile_picture_is_url

        try:
            self.user_repository.update(current_user)
        except IntegrityError:
            raise HTTPException(409, detail="unique field already exists")

    async def update_my_pfp_file(self, current_user: User, file: UploadFile) -> None:
        content, _, ext, _ = await validate_and_read_file(
            file, valid_mime_type="image/", valid_ext=frozenset({"png", "jpg", "jpeg"})
        )

        filename = f"{current_user.id}.{ext}"
        file_path = f"static/image/pfps/{filename}"

        async with aiofiles.open(file_path, "wb") as fp:
            await fp.write(content)

        current_user.profile_picture = file_path
        current_user.profile_picture_is_url = False

        try:
            self.user_repository.update(current_user)
        except IntegrityError as err:
            try:
                await aiofiles_os.remove(file_path)
            except OSError:
                logger.warning(
                    "warn_type=pfp_upload_cleanup_failed ; %s", file_path, exc_info=True
                )
            raise HTTPException(409, detail="unique field already exists") from err

    async def delete_my_profile(self, current_user: User) -> None:
        if current_user.role >= get_user_role_level("executive"):
            raise HTTPException(
                403,
                detail="임원진 이상의 권한은 휴회원으로 전환할 수 없습니다.",
            )
        current_user.role = get_user_role_level("dormant")
        self.user_repository.update(current_user)

        if current_user.discord_id:
            await self.change_discord_role(current_user.discord_id, "dormant")

    async def login(self, body: BodyLogin) -> ResponseLogin:
        expected = generate_user_hash(body.email)
        if not hmac.compare_digest(body.hashToken, expected):
            raise HTTPException(401, detail="invalid hash token")

        user_id = sha256_hash(body.email.lower())
        user = self.user_repository.get_by_id(user_id)

        if user is None:
            raise HTTPException(404, detail="invalid email address")

        user.last_login = utcnow()
        self.user_repository.update(user)

        payload = {
            "user_id": user.id,
            "exp": utcnow() + timedelta(seconds=get_settings().jwt_valid_seconds),
        }
        encoded_jwt = jwt.encode(payload, get_settings().jwt_secret, "HS256")
        return ResponseLogin(jwt=encoded_jwt)

    async def update_user(
        self, current_user: User, id: str, body: BodyUpdateUser
    ) -> None:
        user = self.user_repository.get_by_id(id)
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

        try:
            self.user_repository.update(user)
        except IntegrityError:
            raise HTTPException(409, detail="unique field already exists")

        if body.role:
            logger.info(
                f"info_type=user_role_updated ; user_id={id} ; old_role={old_role} ; new_role={get_user_role_level(body.role)} ; executor={current_user.id}"
            )
            if user.discord_id:
                await self.change_discord_role(user.discord_id, body.role)

    async def change_discord_role(self, discord_id: int, to_role_name: str) -> None:
        """
        Change role of user by removing all possible roles and adding new one.
        """
        for role in self.user_role_repository.list_all():
            await mq_client.send_discord_bot_request_no_reply(
                action_code=2002, body={"user_id": discord_id, "role_name": role.name}
            )
        await mq_client.send_discord_bot_request_no_reply(
            action_code=2001, body={"user_id": discord_id, "role_name": to_role_name}
        )


UserServiceDep = Annotated[UserService, Depends()]


class OldboyService:
    def __init__(
        self,
        user_service: UserServiceDep,
        oldboy_repository: OldboyApplicantRepositoryDep,
        user_repository: UserRepositoryDep,
        user_role_repository: UserRoleRepositoryDep,
    ):
        self.user_service = user_service
        self.oldboy_repository = oldboy_repository
        self.user_repository = user_repository
        self.user_role_repository = user_role_repository

    async def register_applicant(self, current_user: User) -> OldboyApplicant:
        if utcnow() - current_user.created_at < timedelta(weeks=52 * 3):
            raise HTTPException(
                400, detail="must have been a member for at least 3 years."
            )

        if current_user.role != get_user_role_level("member"):
            raise HTTPException(400, detail="must be a member")

        oldboy_applicant = OldboyApplicant(id=current_user.id)

        try:
            oldboy_applicant = self.oldboy_repository.create(oldboy_applicant)
        except IntegrityError:
            raise HTTPException(409, detail="oldboy_applicant already exists")

        return oldboy_applicant

    def get_applicant_self(self, user_id: str) -> OldboyApplicant:
        applicant = self.oldboy_repository.get_by_id(user_id)
        if applicant is None:
            raise HTTPException(404, detail="applicant not found for user")
        return applicant

    def get_all_applicants(self) -> Sequence[OldboyApplicant]:
        return self.oldboy_repository.list_all()

    async def process_applicant(self, id: str) -> None:
        oldboy_applicant = self.oldboy_repository.get_by_id(id)
        if not oldboy_applicant:
            raise HTTPException(404, detail="oldboy_applicant not found")

        user = self.user_repository.get_by_id(id)
        if not user:
            raise HTTPException(503, detail="user does not exist")

        if user.role == get_user_role_level("oldboy"):
            raise HTTPException(409, detail="user is already oldboy")

        oldboy_applicant.processed = True
        user.role = get_user_role_level("oldboy")

        self.oldboy_repository.update(oldboy_applicant)
        self.user_repository.update(user)

        if user.discord_id:
            await self.user_service.change_discord_role(user.discord_id, "oldboy")

    async def delete_applicant_self(self, user_id: str) -> None:
        oldboy_applicant = self.oldboy_repository.get_by_id(user_id)
        if not oldboy_applicant:
            raise HTTPException(404, detail="oldboy_applicant not found")

        if oldboy_applicant.processed:
            raise HTTPException(409, detail="oldboy_applicant already processed")

        self.oldboy_repository.delete(oldboy_applicant)

    async def delete_applicant_executive(self, id: str) -> None:
        user = self.user_repository.get_by_id(id)
        if not user:
            raise HTTPException(404, detail="user does not exist")

        oldboy_applicant = self.oldboy_repository.get_by_id(user.id)
        if not oldboy_applicant:
            raise HTTPException(404, detail="oldboy_applicant not found")

        self.oldboy_repository.delete(oldboy_applicant)

    async def reactivate(self, current_user: User) -> None:
        if current_user.role != get_user_role_level("oldboy"):
            raise HTTPException(400, detail="you are not oldboy")

        current_user.role = get_user_role_level("member")
        current_user.status = UserStatus.pending
        self.user_repository.update(current_user)

        oldboy_applicant = self.oldboy_repository.get_by_id(current_user.id)
        if oldboy_applicant:
            self.oldboy_repository.delete(oldboy_applicant)

        if current_user.discord_id:
            await self.user_service.change_discord_role(
                current_user.discord_id, "member"
            )


OldboyServiceDep = Annotated[OldboyService, Depends()]


class StandbyService:
    def __init__(
        self,
        standby_repository: StandbyReqTblRepositoryDep,
        user_repository: UserRepositoryDep,
    ):
        self.standby_repository = standby_repository
        self.user_repository = user_repository

    def get_standby_list(self) -> Sequence[StandbyReqTbl]:
        return self.standby_repository.list_all()

    async def process_standby_list_manually(
        self, current_user: User, body: ProcessStandbyListManuallyBody
    ) -> None:
        user = self.user_repository.get_by_id(body.id)
        if not user:
            raise HTTPException(404, detail="user not found")
        if user.status == UserStatus.active:
            raise HTTPException(409, detail="the user is already active")

        user.status = UserStatus.active
        self.user_repository.update(user)

        standbyreq = self.standby_repository.get_by_user_id(body.id)

        if standbyreq:
            standbyreq.is_checked = True
            standbyreq.deposit_name = f"Manually by {current_user.name}"
            standbyreq.deposit_time = utcnow()
            self.standby_repository.update(standbyreq)
        else:
            standbyreq = StandbyReqTbl(
                standby_user_id=user.id,
                user_name=user.name,
                deposit_name=f"Manually by {current_user.name}",
                deposit_time=utcnow(),
                is_checked=True,
            )
            self.standby_repository.create(standbyreq)

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
            result = await self._process_single_deposit(deposit)
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
        result = await self._process_single_deposit(body)
        return ProcessDepositResponse(result=result)

    async def _process_single_deposit(
        self, deposit: DepositDTO
    ) -> ProcessDepositResult:
        try:
            if deposit.deposit_name[-2:].isdigit():
                matching_standbyreqs = (
                    self.standby_repository.get_unchecked_by_deposit_name(
                        deposit.deposit_name
                    )
                )  # search on deposit_name, which is "name+last 2 phone number" form
            else:
                matching_standbyreqs = (
                    self.standby_repository.get_unchecked_by_user_name(
                        deposit.deposit_name
                    )
                )  # search on user_name, which is "name" form

            matching_users = []
            for req in matching_standbyreqs:
                u = self.user_repository.get_by_id(req.standby_user_id)
                if u:
                    matching_users.append(UserResponse.model_validate(u))

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
                if deposit.deposit_name[-2:].isdigit():
                    name = deposit.deposit_name[:-2]
                    phone_tail = deposit.deposit_name[-2:]
                    matching_users_error = (
                        self.user_repository.get_by_name_and_phone_tail(
                            name, phone_tail
                        )
                    )
                else:
                    matching_users_error = self.user_repository.get_by_name(
                        deposit.deposit_name
                    )

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
                if user.status not in (UserStatus.pending, UserStatus.standby):
                    logger.error(
                        f"err_type=deposit ; err_code=412 ; msg=user is not in pending or standby status but in {user.status} status ; deposit={deposit} ; users={matching_users}"
                    )
                    return ProcessDepositResult(
                        result_code=412,
                        result_msg=f"해당 입금 기록에 대응하는 사용자의 상태는 {user.status}로 pending 또는 standby 상태가 아닙니다",
                        record=deposit,
                        users=matching_users,
                    )
                if user.status == UserStatus.pending:
                    user.status = UserStatus.standby
                    self.user_repository.update(user)

                new_req = StandbyReqTbl(
                    standby_user_id=user.id,
                    user_name=user.name,
                    deposit_name=f"{user.name}{user.phone[-2:]}",
                    is_checked=False,
                )
                self.standby_repository.create(new_req)
                matching_standbyreqs = [new_req]

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
            user = self.user_repository.get_by_id(stby_user.standby_user_id)
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
            self._verify_enroll_user_ctrl(user, stby_user, deposit)
            logger.info(
                f"info_type=deposit ; deposit={deposit} ; users={matching_users}"
            )
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

    def _verify_enroll_user_ctrl(
        self, user: User, stby_req: StandbyReqTbl, deposit: DepositDTO
    ) -> None:
        user.status = UserStatus.active
        self.user_repository.update(user)
        stby_req.deposit_time = deposit.deposit_time
        stby_req.deposit_name = deposit.deposit_name
        stby_req.is_checked = True
        self.standby_repository.update(stby_req)


StandbyServiceDep = Annotated[StandbyService, Depends()]
