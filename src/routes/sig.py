from typing import Optional, Sequence

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from src.dependencies import SCSCGlobalStatusDep, UserDep
from src.model import SCSCStatus
from src.schemas import SigMemberResponse, SigResponse, SigTagResponse, TagResponse
from src.services import (
    BodyCreateSIG,
    BodyExecutiveJoinSIG,
    BodyExecutiveLeaveSIG,
    BodyHandoverSIG,
    BodyUpdateSIG,
    SigServiceDep,
)

sig_router = APIRouter(tags=["sig"])


class BodyCreateTag(BaseModel):
    text: str = Field(..., min_length=1)
    is_major: bool = False


@sig_router.post("/sig/create", status_code=201)
async def create_sig(
    scsc_global_status: SCSCGlobalStatusDep,
    current_user: UserDep,
    body: BodyCreateSIG,
    sig_service: SigServiceDep,
) -> SigResponse:
    sig = await sig_service.create_sig(scsc_global_status, current_user, body)
    return SigResponse.model_validate(sig)


@sig_router.get("/sig/{id}")
async def get_sig_by_id(id: int, sig_service: SigServiceDep) -> SigResponse:
    return SigResponse.model_validate(sig_service.get_by_id(id))


@sig_router.get("/sigs")
async def get_all_sigs(
    sig_service: SigServiceDep,
    year: Optional[int] = None,
    semester: Optional[int] = None,
    status: Optional[SCSCStatus] = None,
    tag: Optional[list[str]] = Query(None),
) -> Sequence[SigResponse]:
    sigs = sig_service.get_sigs(
        year,
        semester,
        status,
        tag,
    )
    return SigResponse.model_validate_list(sigs)


@sig_router.post("/sig/{id}/update", status_code=204)
async def update_my_sig(
    id: int,
    current_user: UserDep,
    body: BodyUpdateSIG,
    sig_service: SigServiceDep,
):
    await sig_service.update_sig(id, current_user, body, False)


@sig_router.post("/sig/{id}/delete", status_code=204)
async def delete_my_sig(
    id: int,
    current_user: UserDep,
    sig_service: SigServiceDep,
):
    await sig_service.delete_sig(id, current_user, False)


@sig_router.post("/executive/sig/{id}/update", status_code=204)
async def exec_update_sig(
    id: int,
    current_user: UserDep,
    body: BodyUpdateSIG,
    sig_service: SigServiceDep,
):
    await sig_service.update_sig(id, current_user, body, True)


@sig_router.post("/executive/sig/{id}/delete", status_code=204)
async def exec_delete_sig(
    id: int,
    current_user: UserDep,
    sig_service: SigServiceDep,
):
    await sig_service.delete_sig(id, current_user, True)


@sig_router.post("/sig/{id}/handover", status_code=204)
async def handover_sig(
    id: int,
    current_user: UserDep,
    body: BodyHandoverSIG,
    sig_service: SigServiceDep,
) -> None:
    sig_service.handover_sig(id, current_user, body, False)


@sig_router.post("/executive/sig/{id}/handover", status_code=204)
async def executive_handover_sig(
    id: int,
    current_user: UserDep,
    body: BodyHandoverSIG,
    sig_service: SigServiceDep,
) -> None:
    sig_service.handover_sig(id, current_user, body, True)


@sig_router.get("/sig/{id}/members")
async def get_sig_members(
    id: int, sig_service: SigServiceDep
) -> Sequence[SigMemberResponse]:
    return SigMemberResponse.model_validate_list(sig_service.get_members(id))


@sig_router.post("/sig/{id}/member/join", status_code=204)
async def join_sig(
    id: int,
    current_user: UserDep,
    sig_service: SigServiceDep,
):
    await sig_service.join_sig(id, current_user)


@sig_router.post("/sig/{id}/member/leave", status_code=204)
async def leave_sig(
    id: int,
    current_user: UserDep,
    sig_service: SigServiceDep,
):
    await sig_service.leave_sig(id, current_user)


@sig_router.post("/executive/sig/{id}/member/join", status_code=204)
async def executive_join_sig(
    id: int,
    current_user: UserDep,
    body: BodyExecutiveJoinSIG,
    sig_service: SigServiceDep,
):
    await sig_service.executive_join_sig(id, current_user, body)


@sig_router.post("/executive/sig/{id}/member/leave", status_code=204)
async def executive_leave_sig(
    id: int,
    current_user: UserDep,
    body: BodyExecutiveLeaveSIG,
    sig_service: SigServiceDep,
):
    await sig_service.executive_leave_sig(id, current_user, body)


class BodyAddSigTag(BaseModel):
    tag_id: int


@sig_router.post("/sig/{id}/tag", status_code=201)
def add_sig_tag(
    id: int,
    current_user: UserDep,
    body: BodyAddSigTag,
    sig_service: SigServiceDep,
) -> SigTagResponse:
    return SigTagResponse.model_validate(
        sig_service.add_sig_tag(id, body.tag_id, current_user)
    )


@sig_router.get("/sig/{id}/tag")
def get_sig_tags(
    id: int,
    sig_service: SigServiceDep,
) -> Sequence[TagResponse]:
    return TagResponse.model_validate_list(sig_service.get_sig_tags(id))


@sig_router.delete("/sig/{id}/tag/{tag_id}", status_code=204)
def remove_sig_tag(
    id: int,
    tag_id: int,
    current_user: UserDep,
    sig_service: SigServiceDep,
) -> None:
    sig_service.remove_sig_tag(id, tag_id, current_user)


@sig_router.get("/tags")
def get_tags(sig_service: SigServiceDep) -> Sequence[TagResponse]:
    return TagResponse.model_validate_list(sig_service.get_tags())


@sig_router.post("/tag", status_code=201)
def create_tag_by_user(
    body: BodyCreateTag,
    current_user: UserDep,
    sig_service: SigServiceDep,
) -> TagResponse:
    return TagResponse.model_validate(
        sig_service.create_tag_by_user(body.text, current_user)
    )


@sig_router.post("/executive/tag", status_code=201)
def create_tag_by_executive(
    body: BodyCreateTag,
    current_user: UserDep,
    sig_service: SigServiceDep,
) -> TagResponse:
    return TagResponse.model_validate(
        sig_service.create_tag_by_executive(body.text, body.is_major, current_user)
    )


@sig_router.delete("/executive/tag/{tag_id}", status_code=204)
def delete_tag(
    tag_id: int,
    current_user: UserDep,
    sig_service: SigServiceDep,
) -> None:
    sig_service.delete_tag(tag_id, current_user)
