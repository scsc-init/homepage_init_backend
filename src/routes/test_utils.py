from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from src.core import get_settings
from src.dependencies import api_secret
from src.schemas import UserResponse
from src.services import BodyCreateTestUser, TestUserServiceDep


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
) -> list[UserResponse]:
    return test_user_service.list_test_users(email=email, name=name)


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
