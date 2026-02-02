from typing import Annotated, Optional, Sequence

from fastapi import Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import IntegrityError

from src.core import logger
from src.db import SessionDep, get_user_role_level
from src.dependencies import SCSCGlobalStatusDep
from src.model import SCSCStatus, User, UserStatus
from src.repositories import (
    MajorRepositoryDep,
    OldboyApplicantRepositoryDep,
    StandbyReqTblRepositoryDep,
    UserRepositoryDep,
)
from src.schemas import SCSCGlobalStatusResponse, UserResponse
from src.util import (
    get_new_year_semester,
    is_valid_phone,
    is_valid_student_id,
    sha256_hash,
)


class BodyCreateTestUser(BaseModel):
    email: EmailStr
    name: str
    phone: str
    student_id: str
    major_id: int
    role_name: str = "executive"
    status: UserStatus = UserStatus.active
    profile_picture: Optional[str] = None
    profile_picture_is_url: bool = False
    discord_id: Optional[int] = None
    discord_name: Optional[str] = None


class BodyAssignPresident(BaseModel):
    user_id: str


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
            status=body.status,
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
            self.user_repository.delete_all()
        except IntegrityError as exc:
            raise HTTPException(
                409,
                detail="cannot delete user: remove related records first",
            ) from exc

        logger.info("info_type=test_user_all_deleted")

    def assign_president(self, body: BodyAssignPresident) -> UserResponse:
        president_level = get_user_role_level("president")
        user = self.user_repository.get_by_id(body.user_id)
        if not user:
            raise HTTPException(404, detail="user not found")
        if user.role == president_level:
            return UserResponse.model_validate(user)
        user.role = president_level
        self.user_repository.update(user)
        logger.info("info_type=test_president_assigned ; user_id=%s", user.id)
        return UserResponse.model_validate(user)


class TestSemesterService:
    def __init__(self, session: SessionDep, scsc_global_status: SCSCGlobalStatusDep):
        self.session = session
        self.scsc_global_status = scsc_global_status

    def get_semester(self) -> SCSCGlobalStatusResponse:
        return SCSCGlobalStatusResponse.model_validate(self.scsc_global_status)

    def update_semester(self) -> SCSCGlobalStatusResponse:
        status = self.scsc_global_status.status
        if status == SCSCStatus.active:
            new_year, new_semester = get_new_year_semester(
                self.scsc_global_status.year, self.scsc_global_status.semester
            )
            self.scsc_global_status.year = new_year
            self.scsc_global_status.semester = new_semester
            self.scsc_global_status.status = SCSCStatus.recruiting
        elif status == SCSCStatus.recruiting:
            self.scsc_global_status.status = SCSCStatus.active
        elif status == SCSCStatus.inactive:
            self.scsc_global_status.status = SCSCStatus.recruiting
        else:
            raise HTTPException(400, detail="invalid scsc status")
        self.session.add(self.scsc_global_status)
        self.session.commit()
        return SCSCGlobalStatusResponse.model_validate(self.scsc_global_status)


TestUserServiceDep = Annotated[TestUserService, Depends()]
TestSemesterServiceDep = Annotated[TestSemesterService, Depends()]
