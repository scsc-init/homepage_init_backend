from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence

import jwt
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.controller import BodyCreateUser, create_user_ctrl, enroll_user_ctrl, register_oldboy_applicant_ctrl, process_oldboy_applicant_ctrl, reactivate_oldboy_ctrl
from src.core import get_settings
from src.db import SessionDep
from src.model import User, UserStatus, StandbyReqTbl, OldboyApplicant
from src.util import get_user_role_level, is_valid_phone, is_valid_student_id, sha256_hash, get_user, get_file_extension, process_standby_user

user_router = APIRouter(tags=['user'])


@user_router.post('/user/create', status_code=201)
async def create_user(session: SessionDep, body: BodyCreateUser) -> User:
    return await create_user_ctrl(session, body)


@user_router.post('/user/enroll', status_code=204)
async def enroll_user(session: SessionDep, request: Request) -> None:
    current_user = get_user(request)
    return await enroll_user_ctrl(session, current_user.id)


@user_router.get('/user/profile')
async def get_my_profile(request: Request) -> User:
    return get_user(request)


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    major_id: int

    model_config = {
        "from_attributes": True  # enables reading from ORM objects
    }


@user_router.get('/user/{id}', response_model=UserResponse)
async def get_user_by_id(id: str, session: SessionDep) -> UserResponse:
    user = session.get(User, id)
    if not user: raise HTTPException(404, detail="user not found")
    return UserResponse.model_validate(user)


@user_router.get('/users')
async def get_executives(session: SessionDep, user_role: str) -> Sequence[User]:
    level = get_user_role_level(user_role)
    if level < get_user_role_level('executive'):
        raise HTTPException(400, detail="Cannot get users without executive or higher role")
    return session.exec(select(User).where(User.role == level)).all()


class BodyUpdateMyProfile(BaseModel):
    name: str
    phone: str
    student_id: str
    major_id: int


@user_router.post('/user/update', status_code=204)
async def update_my_profile(session: SessionDep, request: Request, body: BodyUpdateMyProfile) -> None:
    current_user = get_user(request)
    if not is_valid_phone(body.phone): raise HTTPException(422, detail="invalid phone number")
    if not is_valid_student_id(body.student_id): raise HTTPException(422, detail="invalid student_id")
    current_user.name = body.name
    current_user.phone = body.phone
    current_user.student_id = body.student_id
    current_user.major_id = body.major_id
    session.add(current_user)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="unique field already exists")
    return


@user_router.post('/user/delete', status_code=204)
async def delete_my_profile(session: SessionDep, request: Request) -> None:
    current_user = get_user(request)
    if current_user.role >= get_user_role_level('executive'): raise HTTPException(403, detail="user whose role is executive or above cannot delete their account")
    session.delete(current_user)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="cannot delete user because of foreign key restriction")
    return


class BodyLogin(BaseModel):
    email: str


class ResponseLogin(BaseModel):
    jwt: str


@user_router.post('/user/login')
async def login(session: SessionDep, body: BodyLogin) -> ResponseLogin:
    result = session.get(User, sha256_hash(body.email.lower()))
    if result is None: raise HTTPException(404, detail="invalid email address")
    result.last_login = datetime.now(timezone.utc)
    session.add(result)
    session.commit()

    payload = {
        "user_id": result.id,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=get_settings().jwt_valid_seconds)
    }
    encoded_jwt = jwt.encode(payload, get_settings().jwt_secret, "HS256")
    return ResponseLogin(jwt=encoded_jwt)


class BodyUpdateUser(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    student_id: Optional[str] = None
    major_id: Optional[int] = None
    role: Optional[str] = None
    status: Optional[UserStatus] = None


@user_router.post('/executive/user/{id}', status_code=204)
async def update_user(id: str, session: SessionDep, request: Request, body: BodyUpdateUser) -> None:
    current_user = get_user(request)
    user = session.get(User, id)
    if user is None: raise HTTPException(404, detail="no user exists")

    if current_user.role <= user.role: raise HTTPException(403, detail="Cannot update user with a higher or equal role than yourself")
    if body.role:
        level = get_user_role_level(body.role)
        if current_user.role < level: raise HTTPException(403, detail="Cannot assign role higher than yours")
        user.role = level

    if body.phone:
        if not is_valid_phone(body.phone): raise HTTPException(422, detail="invalid phone number")
        user.phone = body.phone
    if body.student_id:
        if not is_valid_student_id(body.student_id): raise HTTPException(422, detail="invalid student_id")
        user.student_id = body.student_id

    if body.name: user.name = body.name
    if body.major_id: user.major_id = body.major_id
    if body.status: user.status = body.status

    session.add(user)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="unique field already exists")
    return


@user_router.post('/user/oldboy/register', status_code=201)
async def create_oldboy_applicant(session: SessionDep, request: Request) -> OldboyApplicant:
    current_user = get_user(request)
    return await register_oldboy_applicant_ctrl(session, current_user)


@user_router.get('/executive/user/oldboy/applicants')
async def get_oldboy_applicants(session: SessionDep, processed: bool) -> Sequence[OldboyApplicant]:
    return session.exec(select(OldboyApplicant).where(OldboyApplicant.processed == processed)).all()


@user_router.post('/executive/user/oldboy/{id}/process', status_code=204)
async def process_oldboy_applicant(id: str, session: SessionDep) -> None:
    return await process_oldboy_applicant_ctrl(session, id)


@user_router.post('/user/oldboy/unregister', status_code=204)
async def delete_oldboy_applicant_self(session: SessionDep, request: Request) -> None:
    current_user = get_user(request)
    oldboy_applicant = session.get(OldboyApplicant, current_user.id)
    if not oldboy_applicant: raise HTTPException(404, detail="oldboy_applicant not found")
    session.delete(oldboy_applicant)
    session.commit()
    return


@user_router.post('/executive/user/oldboy/{id}/unregister', status_code=204)
async def delete_oldboy_applicant_executive(id: str, session: SessionDep) -> None:
    user = session.get(User, id)
    if not user: raise HTTPException(404, detail="user does not exist")
    oldboy_applicant = session.get(OldboyApplicant, user.id)
    if not oldboy_applicant: raise HTTPException(404, detail="oldboy_applicant not found")
    session.delete(oldboy_applicant)
    session.commit()
    return


@user_router.post('/user/oldboy/reactivate', status_code=204)
async def reactivate_oldboy(session: SessionDep, request: Request) -> None:
    current_user = get_user(request)
    return await reactivate_oldboy_ctrl(session, current_user)


@user_router.get('/executive/user/standby/list')
async def get_standby_list(session: SessionDep) -> Sequence[StandbyReqTbl]:
    return session.exec(select(StandbyReqTbl)).all()


@user_router.post('/executive/user/standby/process', status_code=204)
async def process_standby_list(session: SessionDep, file: UploadFile = File(...)):
    if file.content_type is None: raise HTTPException(400, detail="cannot upload file without content_type")
    ext_whitelist = ('csv')
    if file.filename is None or get_file_extension(file.filename) not in ext_whitelist: raise HTTPException(400, detail=f"cannot upload if the extension is not {ext_whitelist}")

    try:
        deposit_array = await process_standby_user('utf-8', file)
    except UnicodeDecodeError:
        deposit_array = await process_standby_user('euc-kr', file)
    except Exception as e:
        raise HTTPException(400, detail=f"csv file reading failed with following error: {e}")

    user_array = session.exec(select(User).where(User.status == UserStatus.pending)).all()
    stby_user_array = session.exec(select(StandbyReqTbl)).all()

    for deposit in deposit_array:
        matching_users: list[StandbyReqTbl] = []
        if deposit[2][-2:].isdigit():
            for stby_user in stby_user_array:
                if stby_user.deposit_name == deposit[2]:
                    matching_users.append(stby_user)
        else:
            for stby_user in stby_user_array:
                if stby_user.user_name == deposit[2]:
                    matching_users.append(stby_user)

        if len(matching_users) > 1:
            raise HTTPException(400, f"more than one matching user in standby request db for deposit {deposit}")

        elif len(matching_users) == 1:
            if deposit[0] < get_settings().enrollment_fee:
                raise HTTPException(400, f"Insufficient funds from {deposit}")
            elif deposit[0] > get_settings().enrollment_fee:
                raise HTTPException(400, f"Oversufficient funds from {deposit}")

            stby_user = matching_users[0]
            if stby_user.is_checked: return
            user = session.get(User, stby_user.standby_user_id)
            user.status = UserStatus.active
            stby_user.request_time = deposit[1]
            stby_user.is_checked = True
            session.add(user)
            session.add(stby_user)
            session.commit()

        elif len(matching_users) == 0:
            matching_users_error: list[User] = []
            if deposit[2][-2:].isdigit():
                for user in user_array:
                    if deposit[2][:-2] == user.name and deposit[2][-2:] == user.phone[-2:]:
                        matching_users_error.append(stby_user)
            else:
                for user in user_array:
                    if deposit[2] == user.name:
                        matching_users_error.append(stby_user)

            if len(matching_users_error) > 1 or len(matching_users_error) == 0:
                raise HTTPException(400, detail=f"no matching user in standby request db for deposit {deposit}")

            await enroll_user_ctrl(session, user.id)
            user.status = UserStatus.active
            stby_tbl = session.get(StandbyReqTbl, user.id)
            stby_tbl.request_time = deposit[1]
            stby_tbl.is_checked = True
            session.add(user)
            session.add(stby_tbl)
            session.commit()
    return