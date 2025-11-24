from typing import Sequence

from fastapi import APIRouter

from src.controller import BodyCreateMajor, MajorServiceDep
from src.model import Major
from src.schemas import MajorResponse

major_router = APIRouter(tags=["major"])


@major_router.post("/executive/major/create", status_code=201)
async def create_major(
    body: BodyCreateMajor,
    major_service: MajorServiceDep,
) -> MajorResponse:
    major = major_service.create_major(body)
    return MajorResponse.model_validate(major)


@major_router.get("/majors")
async def get_all_majors(
    major_service: MajorServiceDep,
) -> Sequence[MajorResponse]:
    major_list = major_service.get_all_majors()
    return MajorResponse.model_validate_list(major_list)


@major_router.get("/major/{id}")
async def get_major_by_id(
    id: int,
    major_service: MajorServiceDep,
) -> MajorResponse:
    major = major_service.get_major_by_id(id)
    return MajorResponse.model_validate(major)


@major_router.post("/executive/major/update/{id}", status_code=204)
async def update_major(
    id: int,
    body: BodyCreateMajor,
    major_service: MajorServiceDep,
) -> None:
    major_service.update_major(id, body)


@major_router.post("/executive/major/delete/{id}", status_code=204)
async def delete_major(
    id: int,
    major_service: MajorServiceDep,
) -> None:
    major_service.delete_major(id)
