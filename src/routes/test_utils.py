from typing import Optional, Sequence

from fastapi import APIRouter, Depends, HTTPException

from src.core import get_settings
from src.dependencies import api_secret
from src.schemas import SCSCGlobalStatusResponse, UserResponse
from src.services import (
    BodyAssignPresident,
    BodyCreateTestUser,
    TestSemesterServiceDep,
    TestUserServiceDep,
)


def _ensure_test_routes_enabled() -> None:
    if not get_settings().enable_test_routes:
        raise HTTPException(status_code=404, detail="Not found")


test_router = APIRouter(tags=["test"], dependencies=[Depends(api_secret)])


@test_router.get("/users")
async def list_test_users(
    test_user_service: TestUserServiceDep,
    _: None = Depends(_ensure_test_routes_enabled),
    email: Optional[str] = None,
    name: Optional[str] = None,
) -> Sequence[UserResponse]:
    return test_user_service.list_test_users(email=email, name=name)


@test_router.post("/president", status_code=200)
async def create_president(
    body: BodyAssignPresident,
    test_user_service: TestUserServiceDep,
    _: None = Depends(_ensure_test_routes_enabled),
) -> UserResponse:
    return test_user_service.assign_president(body)


@test_router.post("/users", status_code=201)
async def create_test_user(
    body: BodyCreateTestUser,
    test_user_service: TestUserServiceDep,
    _: None = Depends(_ensure_test_routes_enabled),
) -> UserResponse:
    return test_user_service.create_test_user(body)


@test_router.delete("/users/{user_id}", status_code=204)
async def delete_test_user(
    user_id: str,
    test_user_service: TestUserServiceDep,
    _: None = Depends(_ensure_test_routes_enabled),
) -> None:
    test_user_service.delete_test_user(user_id)


@test_router.delete("/users", status_code=204)
async def delete_test_user_all(
    test_user_service: TestUserServiceDep,
    _: None = Depends(_ensure_test_routes_enabled),
) -> None:
    test_user_service.delete_test_user_all()


@test_router.get("/semester")
async def get_test_semester(
    test_semester_service: TestSemesterServiceDep,
    _: None = Depends(_ensure_test_routes_enabled),
) -> SCSCGlobalStatusResponse:
    return test_semester_service.get_semester()


@test_router.post("/semester")
async def update_test_semester(
    test_semester_service: TestSemesterServiceDep,
    _: None = Depends(_ensure_test_routes_enabled),
) -> SCSCGlobalStatusResponse:
    return test_semester_service.update_semester()
