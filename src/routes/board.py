from datetime import datetime, timezone
from typing import Optional, Sequence
import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.db import SessionDep
from src.model import Board
from src.util import get_user

logger = logging.getLogger("app")

board_router = APIRouter(tags=['board'])


class BodyCreateBoard(BaseModel):
    name: str
    description: str
    writing_permission_level: int
    reading_permission_level: int


@board_router.post('/executive/board/create', status_code=201)
async def create_board(session: SessionDep, request: Request, body: BodyCreateBoard) -> Board:
    current_user = get_user(request)
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
        logger.warning(f'err_type=board_update err_code=409 ; msg=unique field already exists ; executor={current_user.id}')
        raise HTTPException(status_code=409, detail="unique field already exists")
    session.refresh(board)
    logger.info(f'info_type=board_update ; board_id={board.id} ; name={body.name} ; description={body.description} ; writing_permission={body.writing_permission_level} ; reading_permission={body.reading_permission_level} ; executor={current_user.id}')
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
    name: Optional[str] = None
    description: Optional[str] = None
    writing_permission_level: Optional[int] = None
    reading_permission_level: Optional[int] = None


@board_router.post('/executive/board/update/{id}', status_code=204)
async def update_board(id: int, session: SessionDep, request: Request, body: BodyUpdateArticle) -> None:
    current_user = get_user(request)
    board = session.get(Board, id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found",)
    # TODO: Who can, What can?
    if body.name: board.name = body.name
    if body.description: board.description = body.description
    if body.writing_permission_level: board.writing_permission_level = body.writing_permission_level
    if body.reading_permission_level: board.reading_permission_level = body.reading_permission_level
    board.updated_at = datetime.now(timezone.utc)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        logger.warning(f'err_type=board_update err_code=409 ; msg=unique field already exists ; board_id={id} ; executor={current_user.id}')
        raise HTTPException(409, detail="unique field already exists")
    logger.info(f'info_type=board_update ; board_id={id} ; name={body.name} ; description={body.description} ; writing_permission={body.writing_permission_level} ; reading_permission={body.reading_permission_level} ; executor={current_user.id}')


@board_router.post('/executive/board/delete/{id}', status_code=204)
async def delete_board(id: int, session: SessionDep, request: Request) -> None:
    current_user = get_user(request)
    board = session.get(Board, id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found",)
    # TODO: Who can, What can?
    session.delete(board)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        logger.warning(f'err_type=board_delete err_code=409 ; msg=Cannot delete board because of foreign key restriction ; board_id={id} ; executor={current_user.id}')
        raise HTTPException(409, detail="Cannot delete board because of foreign key restriction")
    session.refresh(board)
    logger.info(f'info_type=board_delete ; board_id={id} ; executor={current_user.id}')
