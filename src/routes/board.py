from datetime import datetime, timezone
from typing import Optional, Sequence

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.auth import get_current_user
from src.db import SessionDep
from src.model import Article, User, UserRole, Board

boardRouter = APIRouter(prefix="/board", tags=['board'])

class BodyCreateBoard(BaseModel):
    title: str
    description: str
    writing_permission_level: int
    reading_permission_level: int


@boardRouter.post('/create', status_code=201)
async def createBoard(body: BodyCreateBoard, session: SessionDep, currentUser: User = Depends(get_current_user)) -> Article:
    board = Board(
        title=body.title,
        description=body.description,
        writing_permission_level=body.writing_permission_level,
        reading_permission_level=body.reading_permission_level,
    )
    if board.reading_permission_level > int(currentUser.role) < board.writing_permission_level or int(currentUser.role) < 1:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to make this board",
        )
    session.add(board)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="unique field already exists"
        )
    session.refresh(board)
    return board

class BodyUpdateArticle(BaseModel):
    id: int
    title: str
    content: str
    writing_permission_level: int
    reading_permission_level: int

@boardRouter.post('/update/{id}', status_code=204)
async def updateBoard(id: int, body: BodyUpdateArticle, session: SessionDep, currentUser: User = Depends(get_current_user)) -> None:
    board = session.get(Board, id)
    if not board:
        raise HTTPException(
            status_code=404,
            detail="Board not found",
        )
    # TODO: Who can, What can?
    board.title = body.title
    board.content = body.content
    board.writing_permission_level = body.writing_permission_level
    board.reading_permission_level = body.reading_permission_level
    board.updated_at = datetime.now(timezone.utc)
    session.flush()


@boardRouter.post('/delete/{id}', status_code=204)
async def deleteBoard(id: int, session: SessionDep, currentUser: User = Depends(get_current_user)) -> None:
    board = session.get(Board, id)
    if not board:
        raise HTTPException(
            status_code=404,
            detail="Board not found",
        )
    # TODO: Who can, What can?
    session.delete(board)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="Cannot delete user because of foreign key restriction")


@boardRouter.get('/{id}')
async def getBoardById(id: int, session: SessionDep) -> Board:
    board = session.get(Board, id)
    if not board: raise HTTPException(404, detail="Board not found")
    return board


@boardRouter.get('/list')
async def getBoardList(session: SessionDep) -> Board:
    boards = session.exec(select(Board))
    return boards.all()


