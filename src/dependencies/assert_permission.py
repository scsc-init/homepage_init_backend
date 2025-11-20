from fastapi import HTTPException, Request

from src.util import get_user_role_level

from .user_auth import UserSafeDep


async def assert_permission(request: Request, current_user: UserSafeDep):
    if not request.url.path.startswith("/api") or request.method not in (
        "GET",
        "POST",
    ):
        return
    if request.url.path.startswith("/api/executive"):
        if current_user is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        if current_user.role < get_user_role_level("executive"):
            raise HTTPException(
                status_code=403,
                detail="Permission denied: at least executive role required",
            )
    return
