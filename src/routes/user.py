from datetime import datetime, timezone
from typing import Optional, Sequence

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.auth import get_current_user
from src.db import SessionDep
from src.model import User, UserRole, UserStatus
from src.util import is_valid_phone, is_valid_student_id, sha256_hash

user_router = APIRouter(tags=['user'])


class BodyCreateUser(BaseModel):
    email: str
    name: str
    phone: str
    student_id: str
    major_id: int


@user_router.post('/user/create', status_code=201)
async def create_user(body: BodyCreateUser, session: SessionDep) -> User:
    if not is_valid_phone(body.phone): raise HTTPException(422, detail="invalid phone number")
    if not is_valid_student_id(body.student_id): raise HTTPException(422, detail="invalid student_id")
    user = User(
        id=sha256_hash(body.email.lower()),
        email=body.email,
        name=body.name,
        phone=body.phone,
        student_id=body.student_id,
        major_id=body.major_id
    )
    session.add(user)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="unique field already exists")
    session.refresh(user)
    return user


@user_router.get('/user/profile')
async def get_my_profile(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@user_router.get('/user/executives')
async def get_executives(session: SessionDep) -> Sequence[User]:
    return session.exec(select(User).where(User.role == UserRole.executive)).all()


@user_router.get('/user/presidents')
async def get_presidents(session: SessionDep) -> Sequence[User]:
    return session.exec(select(User).where(User.role == UserRole.president)).all()


class BodyUpdateMyProfile(BaseModel):
    name: str
    phone: str
    student_id: str
    major_id: int


@user_router.post('/user/update', status_code=204)
async def update_my_profile(body: BodyUpdateMyProfile, session: SessionDep, current_user: User = Depends(get_current_user)) -> None:
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
async def delete_my_profile(session: SessionDep, current_user: User = Depends(get_current_user)) -> None:
    if current_user.role != UserRole.user: raise HTTPException(403, detail="user whose role is executive or above cannot delete their account")
    session.delete(current_user)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="cannot delete user because of foreign key restriction")
    return


class BodyLogin(BaseModel):
    email: str


@user_router.post('/user/login', status_code=204)
async def login(body: BodyLogin, request: Request, session: SessionDep) -> None:
    result = session.get(User, sha256_hash(body.email.lower()))
    if result is None: raise HTTPException(404, detail="invalid email address")
    result.last_login = datetime.now(timezone.utc)
    session.add(result)
    session.commit()
    request.session['user_id'] = result.id
    return


@user_router.post('/user/logout', status_code=204)
async def logout(request: Request, current_user: User = Depends(get_current_user)) -> None:
    if request.session.get('user_id') != current_user.id: raise HTTPException(500, detail="Session user_id mismatch")
    del request.session['user_id']
    return


class BodyUpdateUser(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    student_id: Optional[str] = None
    major_id: Optional[int] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


@user_router.post('/executive/user/{id}', status_code=204)
async def update_user(id: str, body: BodyUpdateUser, session: SessionDep, current_user: User = Depends(get_current_user)) -> None:
    user = session.get(User, id)
    if user is None: raise HTTPException(404, detail="no user exists")

    if current_user.role <= user.role: raise HTTPException(403, detail="Cannot update user with a higher or equal role than yourself")
    if body.role:
        if current_user.role < body.role: raise HTTPException(403, detail="Cannot assign role higher than yours")
        user.role = body.role

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
