from datetime import datetime, timezone
from typing import Sequence

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.db import SessionDep
from src.model import Board

board_router = APIRouter(tags=['board'])


class BodyCreateBoard(BaseModel):
    name: str
    description: str
    writing_permission_level: int
    reading_permission_level: int


@board_router.post('/executive/board/create', status_code=201)
async def create_board(body: BodyCreateBoard, session: SessionDep) -> Board:
    board = Board(
        name=body.name,
        description=body.description,
        writing_permission_level=body.writing_permission_level,
        reading_permission_level=body.reading_permission_level,
    )
    session.add(board)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="unique field already exists")
    session.refresh(board)
    return board


@board_router.get('/board/{id}')
async def get_board_by_id(id: int, session: SessionDep) -> Board:
    board = session.get(Board, id)
    if not board: raise HTTPException(404, detail="Board not found")
    return board


@board_router.get('/boards')
async def get_board_list(session: SessionDep) -> Sequence[Board]:
    boards = session.exec(select(Board))
    return boards.all()


class BodyUpdateArticle(BaseModel):
    name: str
    description: str
    writing_permission_level: int
    reading_permission_level: int


@board_router.post('/executive/board/update/{id}', status_code=204)
async def update_board(id: int, body: BodyUpdateArticle, session: SessionDep) -> None:
    board = session.get(Board, id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found",)
    # TODO: Who can, What can?
    board.name = body.name
    board.description = body.description
    board.writing_permission_level = body.writing_permission_level
    board.reading_permission_level = body.reading_permission_level
    board.updated_at = datetime.now(timezone.utc)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="unique field already exists")


@board_router.post('/executive/board/delete/{id}', status_code=204)
async def delete_board(id: int, session: SessionDep) -> None:
    board = session.get(Board, id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found",)
    # TODO: Who can, What can?
    session.delete(board)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="Cannot delete user because of foreign key restriction")
