from typing import Annotated, Sequence

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.core import logger
from src.db import SessionDep
from src.model import Major


class BodyCreateMajor(BaseModel):
    college: str
    major_name: str


class MajorService:
    def __init__(self, session: SessionDep):
        self.session = session

    def create_major(self, body: BodyCreateMajor) -> Major:
        major = Major(college=body.college, major_name=body.major_name)
        self.session.add(major)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise HTTPException(409, detail="major already exists")
        self.session.refresh(major)
        logger.info(f"info_type=major_created ; major_id={major.id}")
        return major

    def get_all_majors(self) -> Sequence[Major]:
        return self.session.exec(select(Major)).all()

    def get_major_by_id(self, id: int) -> Major:
        major = self.session.get(Major, id)
        if not major:
            raise HTTPException(404, detail="major not found")
        return major

    def update_major(self, id: int, body: BodyCreateMajor) -> None:
        major = self.session.get(Major, id)
        if not major:
            raise HTTPException(404, detail="major not found")
        major.college = body.college
        major.major_name = body.major_name
        self.session.add(major)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise HTTPException(409, detail="major already exists")
        logger.info(f"info_type=major_updated ; major_id={major.id}")

    def delete_major(self, id: int) -> None:
        major = self.session.get(Major, id)
        if not major:
            raise HTTPException(404, detail="major not found")
        self.session.delete(major)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise HTTPException(
                status_code=400,
                detail="Cannot delete major: it is referenced by existing users",
            )
        logger.info(f"info_type=major_deleted ; major_id={major.id}")


MajorServiceDep = Annotated[MajorService, Depends()]
