from typing import Sequence

from fastapi import APIRouter, Request

from src.controller import BoardServiceDep, BodyCreateBoard, BodyUpdateBoard
from src.model import Board
from src.util import UserDep

board_router = APIRouter(tags=["board"])


@board_router.post("/executive/board/create", status_code=201)
async def create_board(
    request: Request,
    body: BodyCreateBoard,
    board_service: BoardServiceDep,
    current_user: UserDep,
) -> Board:
    return board_service.create_board(
        body=body, current_user=current_user, request=request
    )


@board_router.get("/board/{id}")
async def get_board_by_id(id: int, board_service: BoardServiceDep) -> Board:
    return board_service.get_board_by_id(id=id)


@board_router.get("/boards")
async def get_board_list(board_service: BoardServiceDep) -> Sequence[Board]:
    return board_service.get_board_list()


@board_router.post("/executive/board/update/{id}", status_code=204)
async def update_board(
    id: int,
    request: Request,
    body: BodyUpdateBoard,
    board_service: BoardServiceDep,
    current_user: UserDep,
) -> None:
    board_service.update_board(
        id=id, body=body, current_user=current_user, request=request
    )


@board_router.post("/executive/board/delete/{id}", status_code=204)
async def delete_board(
    id: int,
    request: Request,
    board_service: BoardServiceDep,
    current_user: UserDep,
) -> None:
    board_service.delete_board(id=id, current_user=current_user, request=request)
