from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.db import SessionDep
from src.model import User
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
