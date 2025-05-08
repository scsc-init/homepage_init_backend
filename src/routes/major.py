from typing import Sequence
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

from ..db.engine import SessionDep
from ..model.major import Major


major_router = APIRouter()



class BodyCreateMajor(BaseModel):
    college: str
    major_name: str

@major_router.post('/executive/major/create', tags=['major'], status_code=201)
async def create_major(body: BodyCreateMajor, session: SessionDep) -> Major:
    major = Major(college=body.college, major_name=body.major_name)
    session.add(major)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="major already exists")
    session.refresh(major)
    return major


@major_router.get('/majors', tags=['major'])
async def get_all_majors(session: SessionDep) -> Sequence[Major]:
    return session.exec(select(Major)).all()

@major_router.get('/major/{id}', tags=['major'])
async def get_major_by_id(id: int, session: SessionDep) -> Major:
    major = session.get(Major, id)
    if not major:
        raise HTTPException(status_code=404, detail="major not found")
    return major

    
@major_router.post('/executive/major/update/{id}', tags=['major'], status_code=204)
async def update_major(id: int, body: BodyCreateMajor, session: SessionDep) -> None:
    major = session.get(Major, id)
    if not major:
        raise HTTPException(status_code=404, detail="major not found")
    major.college = body.college
    major.major_name = body.major_name
    session.add(major)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="major already exists")
    return

@major_router.post('/executive/major/delete/{id}', tags=['major'], status_code=204)
async def delete_major(id: int, session: SessionDep) -> None:
    major = session.get(Major, id)
    if not major:
        raise HTTPException(status_code=404, detail="major not found")
    session.delete(major)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete major: it is referenced by existing users"
        )
    return