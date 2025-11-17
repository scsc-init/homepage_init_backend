from typing import Sequence

from fastapi import APIRouter, Request

from src.controller import BoardServiceDep, BodyCreateBoard, BodyUpdateBoard
from src.model import Board
from src.util import UserDep

board_router = APIRouter(tags=["board"])


@board_router.post("/executive/board/create", status_code=201)
async def create_board(
    current_user: UserDep,
    body: BodyCreateBoard,
    board_service: BoardServiceDep,
    request: Request,
) -> Board:
    return board_service.create_board(current_user, body, request)


@board_router.get("/board/{id}")
async def get_board_by_id(id: int, board_service: BoardServiceDep) -> Board:
    return board_service.get_board_by_id(id=id)


@board_router.get("/boards")
async def get_board_list(board_service: BoardServiceDep) -> Sequence[Board]:
    return board_service.get_board_list()


@board_router.post("/executive/board/update/{id}", status_code=204)
async def update_board(
    id: int,
    current_user: UserDep,
    body: BodyUpdateBoard,
    board_service: BoardServiceDep,
    request: Request,
) -> None:
    board_service.update_board(id, current_user, body, request)


@board_router.post("/executive/board/delete/{id}", status_code=204)
async def delete_board(
    id: int,
    current_user: UserDep,
    board_service: BoardServiceDep,
    request: Request,
) -> None:
    board_service.delete_board(id, current_user, request)
