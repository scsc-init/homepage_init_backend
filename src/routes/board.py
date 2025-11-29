from typing import Sequence

from fastapi import APIRouter

from src.dependencies import UserDep
from src.schemas import BoardResponse
from src.services import BoardServiceDep, BodyCreateBoard, BodyUpdateBoard

board_router = APIRouter(tags=["board"])


@board_router.post("/executive/board/create", status_code=201)
async def create_board(
    current_user: UserDep,
    body: BodyCreateBoard,
    board_service: BoardServiceDep,
) -> BoardResponse:
    board = board_service.create_board(current_user, body)
    return BoardResponse.model_validate(board)


@board_router.get("/board/{id}")
async def get_board_by_id(id: int, board_service: BoardServiceDep) -> BoardResponse:
    board = board_service.get_board_by_id(id=id)
    return BoardResponse.model_validate(board)


@board_router.get("/boards")
async def get_board_list(board_service: BoardServiceDep) -> Sequence[BoardResponse]:
    board_list = board_service.get_board_list()
    return BoardResponse.model_validate_list(board_list)


@board_router.post("/executive/board/update/{id}", status_code=204)
async def update_board(
    id: int,
    current_user: UserDep,
    body: BodyUpdateBoard,
    board_service: BoardServiceDep,
) -> None:
    board_service.update_board(id, current_user, body)


@board_router.post("/executive/board/delete/{id}", status_code=204)
async def delete_board(
    id: int,
    current_user: UserDep,
    board_service: BoardServiceDep,
) -> None:
    board_service.delete_board(id, current_user)
