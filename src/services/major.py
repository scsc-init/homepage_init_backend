from typing import Annotated, Sequence

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.core import logger
from src.model import Major
from src.repositories import MajorRepositoryDep


class BodyCreateMajor(BaseModel):
    college: str
    major_name: str


class MajorService:
    def __init__(self, major_repository: MajorRepositoryDep):
        self.major_repository = major_repository

    def create_major(self, body: BodyCreateMajor) -> Major:
        major = Major(college=body.college, major_name=body.major_name)
        try:
            major = self.major_repository.create(major)
        except IntegrityError:
            raise HTTPException(409, detail="major already exists")

        logger.info(f"info_type=major_created ; major_id={major.id}")
        return major

    def get_all_majors(self) -> Sequence[Major]:
        return self.major_repository.list_all()

    def get_major_by_id(self, id: int) -> Major:
        major = self.major_repository.get_by_id(id)
        if not major:
            raise HTTPException(404, detail="major not found")
        return major

    def update_major(self, id: int, body: BodyCreateMajor) -> None:
        major = self.major_repository.get_by_id(id)
        if not major:
            raise HTTPException(404, detail="major not found")

        major.college = body.college
        major.major_name = body.major_name

        try:
            self.major_repository.update(major)
        except IntegrityError:
            raise HTTPException(409, detail="major already exists")

        logger.info(f"info_type=major_updated ; major_id={major.id}")

    def delete_major(self, id: int) -> None:
        major = self.major_repository.get_by_id(id)
        if not major:
            raise HTTPException(404, detail="major not found")

        try:
            self.major_repository.delete(major)
        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete major: it is referenced by existing users",
            )

        logger.info(f"info_type=major_deleted ; major_id={major.id}")


MajorServiceDep = Annotated[MajorService, Depends()]
