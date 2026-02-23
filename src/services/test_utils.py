from typing import Annotated, Optional, Sequence

from fastapi import Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import IntegrityError

from src.core import logger
from src.db import get_user_role_level
from src.model import User
from src.repositories import (
    MajorRepositoryDep,
    OldboyApplicantRepositoryDep,
    StandbyReqTblRepositoryDep,
    UserRepositoryDep,
)
from src.schemas import UserResponse
from src.util import is_valid_phone, is_valid_student_id, sha256_hash


class BodyCreateTestUser(BaseModel):
    email: EmailStr
    name: str
    phone: str
    student_id: str
    major_id: int
    role_name: str = "executive"
    is_active: bool = True
    is_banned: bool = False
    profile_picture: Optional[str] = None
    profile_picture_is_url: bool = False
    discord_id: Optional[int] = None
    discord_name: Optional[str] = None


class TestUserService:
    def __init__(
        self,
        user_repository: UserRepositoryDep,
        major_repository: MajorRepositoryDep,
        standby_repository: StandbyReqTblRepositoryDep,
        oldboy_repository: OldboyApplicantRepositoryDep,
    ) -> None:
        self.user_repository = user_repository
        self.major_repository = major_repository
        self.standby_repository = standby_repository
        self.oldboy_repository = oldboy_repository

    def list_test_users(
        self, email: Optional[str] = None, name: Optional[str] = None
    ) -> Sequence[UserResponse]:
        filters: dict[str, str] = {}
        if email:
            filters["email"] = email
        if name:
            filters["name"] = name
        users = self.user_repository.get_by_filters(filters)
        return UserResponse.model_validate_list(users)

    def create_test_user(self, body: BodyCreateTestUser) -> UserResponse:
        if not is_valid_phone(body.phone):
            raise HTTPException(422, detail="invalid phone number")
        if not is_valid_student_id(body.student_id):
            raise HTTPException(422, detail="invalid student_id")
        if body.profile_picture_is_url and not body.profile_picture:
            raise HTTPException(
                422,
                detail="profile_picture is required when profile_picture_is_url is true",
            )
        if body.is_active and body.is_banned:
            raise HTTPException(
                422,
                detail="invalid status: is_active and is_banned cannot be true at the same time",
            )

        major = self.major_repository.get_by_id(body.major_id)
        if not major:
            raise HTTPException(404, detail="major not found")

        role_level = get_user_role_level(body.role_name)

        user = User(
            id=sha256_hash(body.email.lower()),
            email=body.email,
            name=body.name,
            phone=body.phone,
            student_id=body.student_id,
            role=role_level,
            major_id=body.major_id,
            is_active=body.is_active,
            is_banned=body.is_banned,
            profile_picture=body.profile_picture,
            profile_picture_is_url=body.profile_picture_is_url,
            discord_id=body.discord_id,
            discord_name=body.discord_name,
        )

        try:
            created = self.user_repository.create(user)
        except IntegrityError as exc:
            raise HTTPException(409, detail="unique field already exists") from exc

        logger.info(f"info_type=test_user_created ; user_id={created.id}")
        return UserResponse.model_validate(created)

    def delete_test_user(self, user_id: str) -> None:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(404, detail="user not found")

        standby = self.standby_repository.get_by_user_id(user_id)
        if standby:
            self.standby_repository.delete(standby)

        oldboy = self.oldboy_repository.get_by_id(user_id)
        if oldboy:
            self.oldboy_repository.delete(oldboy)

        try:
            self.user_repository.delete(user)
        except IntegrityError as exc:
            raise HTTPException(
                409,
                detail="cannot delete user: remove related records first",
            ) from exc

        logger.info(f"info_type=test_user_deleted ; user_id={user_id}")

    def delete_test_user_all(self) -> None:
        try:
            self.standby_repository.delete_all()
            self.oldboy_repository.delete_all()
            self.user_repository.delete_all_except_student_ids(
                ["200000001", "200000002"]
            )
        except IntegrityError as exc:
            raise HTTPException(
                409,
                detail="cannot delete user: remove related records first",
            ) from exc

        logger.info("info_type=test_user_all_deleted")


TestUserServiceDep = Annotated[TestUserService, Depends()]
