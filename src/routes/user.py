from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import select
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError

from ..auth.login import get_current_user

from ..core.config import check_frontend_secret

from ..db.engine import SessionDep
from ..model.user import User, UserRole, UserStatus


user_router = APIRouter()



class BodyCreateUser(BaseModel):
    frontend_secret: str
    email: str
    name: str
    phone: str
    student_id: str
    major_id: int

@user_router.post('/user/create', tags=['user'], status_code=201)
async def create_user(body: BodyCreateUser, session: SessionDep) -> User:
    if not check_frontend_secret(body.frontend_secret):
        raise HTTPException(401, detail="frontend_secret unauthorized")
    user = User(
        email=body.email,
        name=body.name,
        phone=body.phone,
        student_id=body.student_id,
        major_id=body.major_id
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail=f"unique field already exists")
    session.refresh(user)
    return user


@user_router.get('/user/profile', tags=['user'])
async def get_my_profile(current_user: User = Depends(get_current_user)) -> User:
    return current_user



class BodyUpdateMyProfile(BaseModel):
    name: str
    phone: str
    student_id: str
    major_id: int

@user_router.post('/user/update', tags=['user'], status_code=204)
async def update_my_profile(body: BodyUpdateMyProfile, session: SessionDep, current_user: User = Depends(get_current_user)) -> None:
    current_user.name = body.name
    current_user.phone = body.phone
    current_user.student_id = body.student_id
    current_user.major_id = body.major_id
    session.add(current_user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail=f"unique field already exists")
    return


@user_router.post('/user/delete', tags=['user'], status_code=204)
async def delete_my_profile(session: SessionDep, current_user: User = Depends(get_current_user)) -> None:
    if current_user.role != UserRole.user:
        raise HTTPException(403, detail="user whose role is executive or above cannot delete their account")
    session.delete(current_user)
    session.commit()
    return


class BodyLogin(BaseModel):
    frontend_secret: str
    email: str

@user_router.post('/user/login', tags=['user'], status_code=204)
async def login(body: BodyLogin, request: Request, session: SessionDep) -> None:
    if not check_frontend_secret(body.frontend_secret):
        raise HTTPException(401, detail="invalid frontend_secret")
    result = session.exec(select(User).where(User.email==body.email)).first()
    if result is None:
        raise HTTPException(404, detail="invalid email address")
    result.last_login = datetime.now(timezone.utc)
    session.add(result)
    session.commit()
    request.session['user_id'] = result.id
    return


@user_router.post('/user/logout', tags=['user'], status_code=204)
async def logout(request: Request, current_user: User = Depends(get_current_user)) -> None:
    if request.session.get('user_id') != current_user.id:
        raise HTTPException(500, detail="Session user_id mismatch")
    del request.session['user_id']
    return


class BodyUpdateUser(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    student_id: Optional[str] = None
    major_id: Optional[int] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None

@user_router.post('/executive/user/{id}', tags=['user'], status_code=204)
async def update_user(id: int, body: BodyUpdateUser, session: SessionDep) -> None:
    user = session.get(User, id)
    if user is None:
        raise HTTPException(404, detail="no user exists")
    if body.name:
        user.name = body.name
    if body.phone:
        user.phone = body.phone
    if body.student_id:
        user.student_id = body.student_id
    if body.major_id:
        user.major_id = body.major_id
    if body.role:
        user.role = body.role
    if body.status:
        user.status = body.status
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail=f"unique field already exists")
    return