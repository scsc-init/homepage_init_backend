import logging

from fastapi import HTTPException, Request

from src.repositories import CheckUserStatusRuleRepositoryDep

from .user_auth import NullableUserDep

logger = logging.getLogger("app")


async def check_user_status(
    request: Request,
    current_user: NullableUserDep,
    check_user_status_rule_repository: CheckUserStatusRuleRepositoryDep,
):
    if current_user and current_user.is_active and not current_user.is_banned:
        return

    blacklist_rules = check_user_status_rule_repository.get_blacklist_rules_by_request(
        request
    )

    if blacklist_rules:
        if current_user is None:
            raise HTTPException(status_code=401, detail="Not authenticated")

        logger.info(
            "info_type=CheckUserStatusMiddleware ; user_id=%s ; status=%s ; method=%s ; path=%s",
            current_user.id,
            "banned" if current_user.is_banned else "inactive",
            request.method,
            request.url.path,
        )
        raise HTTPException(
            status_code=403,
            detail=f"inactive user cannot access path={request.url.path}",
        )

    return
