from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence

import jwt
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.controller import BodyCreateUser, create_user_ctrl, enroll_user_ctrl, register_oldboy_applicant_ctrl, process_oldboy_applicant_ctrl, reactivate_oldboy_ctrl, verify_enroll_user_ctrl
from src.core import get_settings
from src.db import SessionDep
from src.model import User, UserStatus, StandbyReqTbl, OldboyApplicant
from src.util import get_user_role_level, is_valid_phone, is_valid_student_id, sha256_hash, get_user, get_file_extension, process_standby_user, change_discord_role

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
async def get_users(session: SessionDep, email: Optional[str] = None, name: Optional[str] = None, phone: Optional[str] = None, student_id: Optional[str] = None, user_role: Optional[str] = None, status: Optional[str] = None, discord_id: Optional[str] = None, discord_name: Optional[str] = None, major_id: Optional[int] = None) -> Sequence[User]:
    query = select(User)
    if email: query = query.where(User.email == email)
    if name: query = query.where(User.name == name)
    if phone: query = query.where(User.phone == phone)
    if student_id: query = query.where(User.student_id == student_id)
    if user_role: query = query.where(User.role == get_user_role_level(user_role))
    if status: query = query.where(User.status == status)
    if discord_id is not None:
        if discord_id == "": query = query.where(User.discord_id == None)
        else:
            try: query = query.where(User.discord_id == int(discord_id))
            except ValueError: raise HTTPException(422, detail=[{"type": "int_parsing", "loc": ["query", "discord_id"], "msg": "Input should be a valid integer, unable to parse string as an integer", "input": discord_id}])
    if discord_name is not None:
        if discord_name == "": query = query.where(User.discord_name == None)
        else: query = query.where(User.discord_name == discord_name)
    if major_id: query = query.where(User.major_id == major_id)
    return session.exec(query).all()


@user_router.get('/role_names')
async def get_role_names(lang: Optional[str] = "en"):
    if lang == "ko":
        return {"role_names": {"0": "최저권한", "100": "휴회원", "200": "준회원", "300": "정회원", "400": "졸업생", "500": "운영진", "1000": "회장", }}
    else:
        return {"role_names": {"0": "lowest", "100": "dormant", "200": "newcomer", "300": "member", "400": "oldboy", "500": "executive", "1000": "president", }}


class BodyUpdateMyProfile(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    student_id: Optional[str]
    major_id: Optional[int]


@user_router.post('/user/update', status_code=204)
async def update_my_profile(session: SessionDep, request: Request, body: BodyUpdateMyProfile) -> None:
    current_user = get_user(request)
    if body.phone and not is_valid_phone(body.phone): raise HTTPException(422, detail="invalid phone number")
    if body.student_id and not is_valid_student_id(body.student_id): raise HTTPException(422, detail="invalid student_id")
    if body.name: current_user.name = body.name
    if body.phone: current_user.phone = body.phone
    if body.student_id: current_user.student_id = body.student_id
    if body.major_id: current_user.major_id = body.major_id
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
    current_user.role = get_user_role_level('dormant')
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    if current_user.discord_id: await change_discord_role(session, current_user.discord_id, 'dormant')
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
    discord_id: Optional[int] = None
    discord_name: Optional[str] = None


@user_router.post('/executive/user/{id}', status_code=204)
async def update_user(id: str, session: SessionDep, request: Request, body: BodyUpdateUser) -> None:
    current_user = get_user(request)
    user = session.get(User, id)
    if user is None: raise HTTPException(404, detail="no user exists")

    if (current_user.role <= user.role) and not (current_user.role == user.role == 1000): raise HTTPException(403, detail=f"Cannot update user with a higher or equal role than yourself, current role: {current_user.role}, {user.email}, user role: {user.role}")
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
    if body.discord_id: user.discord_id = body.discord_id
    if body.discord_name: user.discord_name = body.discord_name

    session.add(user)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="unique field already exists")
    if body.role:
        session.refresh(user)
        if user.discord_id: await change_discord_role(session, user.discord_id, body.role)
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
    ext_whitelist = ('csv',)

    if file.filename is None or get_file_extension(file.filename) not in ext_whitelist: raise HTTPException(400, detail=f"cannot upload if the extension is not {ext_whitelist}")

    content = await file.read()
    if len(content) > get_settings().file_max_size: raise HTTPException(413, detail=f"cannot upload file larger than {get_settings().file_max_size} bytes")

    try: deposit_array = await process_standby_user('utf-8', content)
    except UnicodeDecodeError: deposit_array = await process_standby_user('euc-kr', content)
    except Exception as e: raise HTTPException(400, detail=f"csv file reading failed with following error: {e}")

    for deposit in deposit_array:
        query_matching_users = select(StandbyReqTbl)
        if deposit.deposit_name[-2:].isdigit(): query_matching_users = query_matching_users.where(StandbyReqTbl.deposit_name == deposit.deposit_name)  # search on deposit_name, which is "name+last 2 phone number" form
        else: query_matching_users = query_matching_users.where(StandbyReqTbl.user_name == deposit.deposit_name)  # search on user_name, which is "name" form
        matching_users = session.exec(query_matching_users).all()

        if len(matching_users) > 1: raise HTTPException(400, f"more than one matching user in standby request db for deposit {deposit}")

        if len(matching_users) == 1:
            if deposit.amount < get_settings().enrollment_fee: raise HTTPException(400, f"Insufficient funds from {deposit}")
            if deposit.amount > get_settings().enrollment_fee: raise HTTPException(400, f"Oversufficient funds from {deposit}")

            stby_user = matching_users[0]
            if stby_user.is_checked: return
            user = session.get(User, stby_user.standby_user_id)
            if not user: raise HTTPException(503, detail="user does not exist")
            await verify_enroll_user_ctrl(session, user, stby_user, deposit.deposit_time)

        elif len(matching_users) == 0:
            query_matching_users_error = select(User)
            if deposit.deposit_name[-2:].isdigit():
                query_matching_users_error = query_matching_users_error.where(
                    User.name == deposit.deposit_name[:-2],
                    func.substring(User.phone, func.length(User.phone) - 1, 2) == deposit.deposit_name[-2:]
                )
            else:
                query_matching_users_error = query_matching_users_error.where(User.name == deposit.deposit_name)
            matching_users_error = session.exec(query_matching_users_error).all()

            if len(matching_users_error) != 1: raise HTTPException(400, detail=f"no matching user in standby request db for deposit {deposit}")

            user = matching_users_error[0]
            await enroll_user_ctrl(session, user.id)
            stby_tbl = session.get(StandbyReqTbl, user.id)
            if not stby_tbl: raise HTTPException(503, detail="stby_tbl does not exist")
            await verify_enroll_user_ctrl(session, user, stby_tbl, deposit.deposit_time)
    return
