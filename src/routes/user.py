from typing import Optional, Sequence

from fastapi import APIRouter, Depends, UploadFile

from src.dependencies import UserDep, api_secret
from src.schemas import PublicUserResponse, UserResponse
from src.services import (
    BodyCreateUser,
    BodyLogin,
    BodyUpdateMyProfile,
    BodyUpdateUser,
    OldboyServiceDep,
    ProcessDepositResponse,
    ProcessStandbyListManuallyBody,
    ProcessStandbyListResponse,
    ResponseLogin,
    StandbyServiceDep,
    UserService,
    UserServiceDep,
)
from src.util import DepositDTO

user_router = APIRouter(tags=["user"])


@user_router.post("/user/create", status_code=201, dependencies=[Depends(api_secret)])
async def create_user(
    body: BodyCreateUser,
    user_service: UserServiceDep,
) -> UserResponse:
    return await user_service.create_user(body)


@user_router.post("/user/login", dependencies=[Depends(api_secret)])
async def login(
    body: BodyLogin,
    user_service: UserServiceDep,
) -> ResponseLogin:
    return await user_service.login(body)


@user_router.post("/user/enroll", status_code=204)
async def enroll_user(
    current_user: UserDep,
    user_service: UserServiceDep,
) -> None:
    await user_service.enroll_user(current_user.id)


@user_router.get("/user/profile")
async def get_my_profile(current_user: UserDep) -> UserResponse:
    return UserResponse.model_validate(current_user)


@user_router.get("/user/executives")
async def get_public_executives(
    user_service: UserServiceDep,
) -> Sequence[PublicUserResponse]:
    return user_service.get_public_executives()


@user_router.get("/executive/users")
async def get_users(
    user_service: UserServiceDep,
    email: Optional[str] = None,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    student_id: Optional[str] = None,
    user_role: Optional[str] = None,
    status: Optional[str] = None,
    discord_id: Optional[str] = None,
    discord_name: Optional[str] = None,
    major_id: Optional[int] = None,
) -> Sequence[UserResponse]:
    return user_service.get_users(
        email,
        name,
        phone,
        student_id,
        user_role,
        status,
        discord_id,
        discord_name,
        major_id,
    )


@user_router.get("/executive/user/{id}", response_model=UserResponse)
async def get_user_by_id(
    id: str,
    user_service: UserServiceDep,
) -> UserResponse:
    return user_service.get_user_by_id(id)


@user_router.get("/role_names")
async def get_role_names(lang: Optional[str] = None):
    return UserService.get_role_names(lang)


@user_router.post("/user/update", status_code=204)
async def update_my_profile(
    current_user: UserDep,
    body: BodyUpdateMyProfile,
    user_service: UserServiceDep,
) -> None:
    await user_service.update_my_profile(current_user, body)


@user_router.post("/user/update-pfp-file", status_code=204)
async def update_my_pfp_file(
    current_user: UserDep,
    file: UploadFile,
    user_service: UserServiceDep,
) -> None:
    await user_service.update_my_pfp_file(current_user, file)


@user_router.post("/user/delete", status_code=204)
async def delete_my_profile(
    current_user: UserDep,
    user_service: UserServiceDep,
) -> None:
    await user_service.delete_my_profile(current_user)


@user_router.post("/executive/user/{id}", status_code=204)
async def update_user(
    id: str,
    current_user: UserDep,
    body: BodyUpdateUser,
    user_service: UserServiceDep,
) -> None:
    await user_service.update_user(current_user, id, body)


@user_router.post("/user/oldboy/register", status_code=201)
async def create_oldboy_applicant(
    current_user: UserDep,
    oldboy_service: OldboyServiceDep,
):
    return await oldboy_service.register_applicant(current_user)


@user_router.get("/user/oldboy/applicant")
async def get_oldboy_applicant_self(
    current_user: UserDep,
    oldboy_service: OldboyServiceDep,
):
    return oldboy_service.get_applicant_self(current_user.id)


@user_router.get("/executive/user/oldboy/applicants")
async def get_oldboy_applicants(
    oldboy_service: OldboyServiceDep,
):
    return oldboy_service.get_all_applicants()


@user_router.post("/executive/user/oldboy/{id}/process", status_code=204)
async def process_oldboy_applicant(
    id: str,
    oldboy_service: OldboyServiceDep,
):
    await oldboy_service.process_applicant(id)


@user_router.post("/user/oldboy/unregister", status_code=204)
async def delete_oldboy_applicant_self(
    current_user: UserDep,
    oldboy_service: OldboyServiceDep,
):
    await oldboy_service.delete_applicant_self(current_user.id)


@user_router.post("/executive/user/oldboy/{id}/unregister", status_code=204)
async def delete_oldboy_applicant_executive(
    id: str,
    oldboy_service: OldboyServiceDep,
):
    await oldboy_service.delete_applicant_executive(id)


@user_router.post("/user/oldboy/reactivate", status_code=204)
async def reactivate_oldboy(
    current_user: UserDep,
    oldboy_service: OldboyServiceDep,
):
    await oldboy_service.reactivate(current_user)


@user_router.get("/executive/user/standby/list")
async def get_standby_list(
    standby_service: StandbyServiceDep,
):
    return standby_service.get_standby_list()


@user_router.post("/executive/user/standby/process/manual", status_code=204)
async def process_standby_list_manually(
    current_user: UserDep,
    body: ProcessStandbyListManuallyBody,
    standby_service: StandbyServiceDep,
):
    await standby_service.process_standby_list_manually(current_user, body)


@user_router.post(
    "/executive/user/standby/process",
    response_model=ProcessStandbyListResponse,
)
async def process_standby_list(
    file: UploadFile,
    standby_service: StandbyServiceDep,
) -> ProcessStandbyListResponse:
    return await standby_service.process_standby_list(file)


@user_router.post(
    "/executive/user/standby/process/deposit",
    response_model=ProcessDepositResponse,
)
async def process_deposit(
    body: DepositDTO,
    standby_service: StandbyServiceDep,
) -> ProcessDepositResponse:
    return await standby_service.process_deposit(body)
