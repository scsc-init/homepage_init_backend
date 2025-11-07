from datetime import datetime, timezone
from typing import Annotated, Optional, Sequence

from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.core import logger
from src.db import SessionDep
from src.model import Board
from src.util import get_user


class BodyCreateBoard(BaseModel):
    name: str
    description: str
    writing_permission_level: int
    reading_permission_level: int


class BodyUpdateBoard(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    writing_permission_level: Optional[int] = None
    reading_permission_level: Optional[int] = None


class BoardService:
    def __init__(
        self,
        session: SessionDep,
    ) -> None:
        self.session = session

    def create_board(self, request: Request, body: BodyCreateBoard) -> Board:
        current_user = get_user(request)
        board = Board(
            name=body.name,
            description=body.description,
            writing_permission_level=body.writing_permission_level,
            reading_permission_level=body.reading_permission_level,
        )
        self.session.add(board)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            logger.warning(
                f"err_type=board_update err_code=409 ; msg=unique field already exists ; executor={current_user.id}"
            )
            raise HTTPException(status_code=409, detail="unique field already exists")
        self.session.refresh(board)
        logger.info(
            f"info_type=board_update ; board_id={board.id} ; name={body.name} ; description={body.description} ; writing_permission={body.writing_permission_level} ; reading_permission={body.reading_permission_level} ; executor={current_user.id}"
        )
        return board

    def get_board_by_id(
        self,
        id: int,
    ) -> Board:
        board = self.session.get(Board, id)
        if not board:
            raise HTTPException(404, detail="Board not found")
        return board

    def get_board_list(
        self,
    ) -> Sequence[Board]:
        boards = self.session.exec(select(Board))
        return boards.all()

    def update_board(self, id: int, request: Request, body: BodyUpdateBoard) -> None:
        current_user = get_user(request)
        board = self.session.get(Board, id)
        if not board:
            raise HTTPException(
                status_code=404,
                detail="Board not found",
            )
        # TODO: Who can, What can?
        if body.name is not None:
            board.name = body.name
        if body.description is not None:
            board.description = body.description
        if body.writing_permission_level is not None:
            board.writing_permission_level = body.writing_permission_level
        if body.reading_permission_level is not None:
            board.reading_permission_level = body.reading_permission_level
        board.updated_at = datetime.now(timezone.utc)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            logger.warning(
                f"err_type=board_update err_code=409 ; msg=unique field already exists ; board_id={id} ; executor={current_user.id}"
            )
            raise HTTPException(409, detail="unique field already exists")
        logger.info(
            f"info_type=board_update ; board_id={id} ; name={body.name} ; description={body.description} ; writing_permission={body.writing_permission_level} ; reading_permission={body.reading_permission_level} ; executor={current_user.id}"
        )

    def delete_board(self, id: int, request: Request) -> None:
        current_user = get_user(request)
        board = self.session.get(Board, id)
        if not board:
            raise HTTPException(
                status_code=404,
                detail="Board not found",
            )
        # TODO: Who can, What can?
        self.session.delete(board)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            logger.warning(
                f"err_type=board_delete err_code=409 ; msg=Cannot delete board because of foreign key restriction ; board_id={id} ; executor={current_user.id}"
            )
            raise HTTPException(
                409, detail="Cannot delete board because of foreign key restriction"
            )
        logger.info(
            f"info_type=board_delete ; board_id={id} ; executor={current_user.id}"
        )


BoardServiceDep = Annotated[BoardService, Depends()]
