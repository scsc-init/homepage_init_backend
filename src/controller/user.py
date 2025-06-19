from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.db import SessionDep
from src.model import User, UserStatus, OldboyApplicant
from src.util import is_valid_phone, is_valid_student_id, sha256_hash, get_user_role_level


class BodyCreateUser(BaseModel):
    email: str
    name: str
    phone: str
    student_id: str
    major_id: int


async def create_user_controller(session: SessionDep, body: BodyCreateUser) -> User:
    if not is_valid_phone(body.phone): raise HTTPException(422, detail="invalid phone number")
    if not is_valid_student_id(body.student_id): raise HTTPException(422, detail="invalid student_id")
    user = User(
        id=sha256_hash(body.email.lower()),
        email=body.email,
        name=body.name,
        phone=body.phone,
        student_id=body.student_id,
        role=get_user_role_level('newcomer'),
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


async def enroll_user_controller(session: SessionDep, user_id: str) -> None:
    user = session.get(User, user_id)
    if not user: raise HTTPException(404, detail="user not found")
    if user.status != UserStatus.pending: raise HTTPException(400, detail="Only user with pending status can enroll")
    user.status = UserStatus.active
    session.add(user)
    session.commit()
    return


async def register_oldboy_applicant_controller(session: SessionDep, user: User) -> OldboyApplicant:
    user_created_at_aware = user.created_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - user_created_at_aware < timedelta(weeks=52 * 3): raise HTTPException(400, detail="lack of qualifications")
    oldboy_applicant = OldboyApplicant(id=user.id)
    session.add(oldboy_applicant)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="oldboy_applicant already exists")
    session.refresh(oldboy_applicant)
    return oldboy_applicant


async def process_oldboy_applicant_controller(session: SessionDep, user_id: str) -> None:
    oldboy_applicant = session.get(OldboyApplicant, user_id)
    if not oldboy_applicant: raise HTTPException(404, detail="oldboy_applicant not found")

    user = session.get(User, user_id)
    if not user: raise HTTPException(503, detail="user does not exist")
    if user.role == get_user_role_level('oldboy'): raise HTTPException(503, detail="user is already oldboy")

    oldboy_applicant.processed = True
    session.add(oldboy_applicant)
    user.role = get_user_role_level('oldboy')
    session.add(user)
    session.commit()
    return
