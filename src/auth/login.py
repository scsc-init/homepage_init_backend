from fastapi import HTTPException, Request

from src.db import SessionDep
from src.model import User


def get_current_user(request: Request, session: SessionDep) -> User:
    user = request.state.user
    if not user: raise HTTPException(401, detail="Not logged in")
    return user
