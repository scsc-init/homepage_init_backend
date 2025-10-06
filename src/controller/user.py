import logging
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.core import get_settings
from src.db import SessionDep
from src.model import (OldboyApplicant, StandbyReqTbl, User, UserResponse,
                       UserStatus)
from src.util import (DepositDTO, change_discord_role, get_user_role_level,
                      is_valid_img_url, is_valid_phone, is_valid_student_id,
                      sha256_hash)

logger = logging.getLogger("app")


class BodyCreateUser(BaseModel):
    email: str
    name: str
    phone: str
    student_id: str
    major_id: int
    profile_picture: str
    profile_picture_is_url: bool


async def create_user_ctrl(session: SessionDep, body: BodyCreateUser) -> User:
    if not is_valid_phone(body.phone):
        raise HTTPException(422, detail="invalid phone number")
    if not is_valid_student_id(body.student_id):
        raise HTTPException(422, detail="invalid student_id")
    if not is_valid_img_url(body.profile_picture):
        raise HTTPException(400, detail="invalid image url")

    user = User(
        id=sha256_hash(body.email.lower()),
        email=body.email,
        name=body.name,
        phone=body.phone,
        student_id=body.student_id,
        role=get_user_role_level('newcomer'),
        major_id=body.major_id,
        profile_picture=body.profile_picture,
        profile_picture_is_url=body.profile_picture_is_url,
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="unique field already exists")
    session.refresh(user)
    logger.info(f'info_type=user_created ; user_id={user.id}')
    return user


async def enroll_user_ctrl(session: SessionDep, user_id: str) -> StandbyReqTbl:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, detail="user not found")
    if user.status != UserStatus.pending:
        raise HTTPException(
            400, detail="Only user with pending status can enroll")
    user.status = UserStatus.standby
    session.add(user)
    stby_req_tbl = StandbyReqTbl(
        standby_user_id=user.id,
        user_name=user.name,
        deposit_name=f'{user.name}{user.phone[-2:]}',
        is_checked=False
    )
    session.add(stby_req_tbl)
    session.commit()
    session.refresh(stby_req_tbl)
    logger.info(f'info_type=user_enrolled ; user_id={user_id}')
    return stby_req_tbl


async def verify_enroll_user_ctrl(session: SessionDep, user: User, stby_req: StandbyReqTbl, deposit: DepositDTO) -> None:
    user.status = UserStatus.active
    stby_req.deposit_time = deposit.deposit_time
    stby_req.deposit_name = deposit.deposit_name
    stby_req.is_checked = True
    session.add(user)
    session.add(stby_req)
    session.commit()
    return


class ProcessDepositResult(BaseModel):
    result_code: int
    result_msg: str
    record: DepositDTO
    users: list[UserResponse]


async def process_deposit_ctrl(session: SessionDep, deposit: DepositDTO) -> ProcessDepositResult:
    try:
        query_standbyreq = select(StandbyReqTbl).where(
            StandbyReqTbl.is_checked == False)
        if deposit.deposit_name[-2:].isdigit():
            # search on deposit_name, which is "name+last 2 phone number" form
            query_standbyreq = query_standbyreq.where(
                StandbyReqTbl.deposit_name == deposit.deposit_name)
        else:
            # search on user_name, which is "name" form
            query_standbyreq = query_standbyreq.where(
                StandbyReqTbl.user_name == deposit.deposit_name)
        matching_standbyreqs = session.exec(query_standbyreq).all()
        matching_users = [UserResponse.model_validate(session.get(
            User, u.standby_user_id)) for u in matching_standbyreqs]

        if len(matching_standbyreqs) > 1:  # multiple standby request found
            logger.error(
                f"err_type=deposit ; err_code=409 ; msg={len(matching_standbyreqs)}users match the following deposit record ; deposit={deposit} ; users={matching_users}")
            return (ProcessDepositResult(
                result_code=409,
                result_msg=f"해당 입금 기록에 대응하는 사용자가 입금 대기자 명단에 {len(matching_standbyreqs)}건 존재합니다",
                record=deposit,
                users=matching_users))

        if len(matching_standbyreqs) == 0:
            query_matching_users_error = select(User)
            if deposit.deposit_name[-2:].isdigit():
                query_matching_users_error = query_matching_users_error.where(
                    User.name == deposit.deposit_name[:-2],
                    func.substring(User.phone, func.length(
                        User.phone) - 1, 2) == deposit.deposit_name[-2:]
                )
            else:
                query_matching_users_error = query_matching_users_error.where(
                    User.name == deposit.deposit_name)
            matching_users_error = session.exec(
                query_matching_users_error).all()
            matching_users = [UserResponse.model_validate(
                u) for u in matching_users_error]

            if len(matching_users_error) != 1:
                if len(matching_users_error) > 1:
                    logger.error(
                        f"err_type=deposit ; err_code=409 ; msg={len(matching_users_error)}users match the following deposit record ; deposit={deposit} ; users={matching_users}")
                    return (ProcessDepositResult(
                        result_code=409,
                        result_msg=f"해당 입금 기록에 대응하는 사용자가 사용자 테이블에 {len(matching_users_error)}건 존재합니다",
                        record=deposit,
                        users=matching_users
                    ))

                # else
                logger.error(
                    f"err_type=deposit ; err_code=404 ; msg=no users match the following deposit record ; deposit={deposit} ; users={matching_users}")
                return (ProcessDepositResult(
                    result_code=404,
                    result_msg="해당 입금 기록에 대응하는 사용자가 사용자 테이블에 존재하지 않습니다",
                    record=deposit,
                    users=matching_users
                ))

            user = matching_users_error[0]
            if user.status != UserStatus.pending:
                logger.error(
                    f"err_type=deposit ; err_code=412 ; msg=user is not in pending status but in {user.status} status ; deposit={deposit} ; users={matching_users}")
                return (ProcessDepositResult(
                    result_code=412,
                    result_msg=f"해당 입금 기록에 대응하는 사용자의 상태는 {user.status}로 pending 상태가 아닙니다",
                    record=deposit,
                    users=matching_users))
            matching_standbyreqs = [await enroll_user_ctrl(session, user.id)]

        # len(matching_standbyreqs) == 1:
        if deposit.amount < get_settings().enrollment_fee:
            logger.error(
                f"err_type=deposit ; err_code=402 ; msg=deposit amount is less than the required {get_settings().enrollment_fee} won ; deposit={deposit} ; users={matching_users}")
            return (ProcessDepositResult(
                result_code=402,
                result_msg=f"입금액이 {get_settings().enrollment_fee}원보다 적습니다",
                record=deposit,
                users=matching_users))
        if deposit.amount > get_settings().enrollment_fee:
            logger.error(
                f"err_type=deposit ; err_code=413 ; msg=deposit amount is more than the required {get_settings().enrollment_fee} won ; deposit={deposit} ; users={matching_users}")
            return (ProcessDepositResult(
                result_code=413,
                result_msg=f"입금액이 {get_settings().enrollment_fee}원보다 많습니다",
                record=deposit,
                users=matching_users))

        stby_user = matching_standbyreqs[0]
        user = session.get(User, stby_user.standby_user_id)
        if not user:
            logger.error(
                f"err_type=deposit ; err_code=500 ; msg=unexpected error: user not found in user table ; deposit={deposit} ; users={matching_users}")
            return (ProcessDepositResult(
                result_code=500,
                result_msg="알 수 없는 오류: user not found in user table",
                record=deposit,
                users=matching_users))
        if user.status != UserStatus.standby:
            logger.error(
                f"err_type=deposit ; err_code=412 ; msg=user is not in standby status but in {user.status} status ; deposit={deposit} ; users={matching_users}")
            return (ProcessDepositResult(
                result_code=412,
                result_msg=f"해당 입금 기록에 대응하는 사용자의 상태는 {user.status}로 standby 상태가 아닙니다",
                record=deposit,
                users=matching_users))
        await verify_enroll_user_ctrl(session, user, stby_user, deposit)
        logger.info(
            f'info_type=deposit ; deposit={deposit} ; users={matching_users}')
        return (ProcessDepositResult(
            result_code=200,
            result_msg="성공",
            record=deposit,
            users=matching_users))
    except Exception as e:
        logger.error(
            f"err_type=deposit ; err_code=500 ; msg=unexpected error: {e} ; deposit={deposit}")
        return (ProcessDepositResult(
            result_code=500,
            result_msg=f"알 수 없는 오류: {e}",
            record=deposit,
            users=[]))


async def register_oldboy_applicant_ctrl(session: SessionDep, user: User) -> OldboyApplicant:
    user_created_at_aware = user.created_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - user_created_at_aware < timedelta(weeks=52 * 3):
        raise HTTPException(
            400, detail="must have been a member for at least 3 years.")
    if user.role != get_user_role_level('member'):
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
    if user.role == get_user_role_level('oldboy'):
        raise HTTPException(409, detail="user is already oldboy")

    oldboy_applicant.processed = True
    session.add(oldboy_applicant)
    user.role = get_user_role_level('oldboy')
    session.add(user)
    session.commit()
    if user.discord_id:
        await change_discord_role(session, user.discord_id, 'oldboy')
    return


async def reactivate_oldboy_ctrl(session: SessionDep, user: User) -> None:
    if user.role != get_user_role_level('oldboy'):
        raise HTTPException(400, detail="you are not oldboy")

    user.role = get_user_role_level('member')
    user.status = UserStatus.pending
    session.add(user)

    oldboy_applicant = session.get(OldboyApplicant, user.id)
    if oldboy_applicant:
        session.delete(oldboy_applicant)

    if user.discord_id:
        await change_discord_role(session, user.discord_id, 'member')
    session.commit()
    return
