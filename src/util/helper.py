from fastapi import HTTPException, Request

from src.model import User


def get_file_extension(filename: str) -> str:
    return filename.split('.')[-1].lower()


def get_user(request: Request) -> User:
    user = request.state.user
    if not user: raise HTTPException(401, detail="Not logged in")
    return user
