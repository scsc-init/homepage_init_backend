import logging

from fastapi import HTTPException, Request

from src.repositories import CheckUserStatusRuleRepositoryDep

from .user_auth import UserSafeDep

logger = logging.getLogger("app")


async def check_user_status(
    request: Request,
    current_user: UserSafeDep,
    check_user_status_rule_repository: CheckUserStatusRuleRepositoryDep,
):
    blacklist_rules = check_user_status_rule_repository.get_blacklist_rules_by_request(
        request
    )

    if blacklist_rules:
        if current_user is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        for rule in blacklist_rules:
            if rule.user_status == current_user.status:
                logger.info(
                    "info_type=CheckUserStatusMiddleware ; user_id=%s ; status=%s ; method=%s ; path=%s",
                    current_user.id,
                    current_user.status,
                    request.method,
                    request.url.path,
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"cannot access path={request.url.path} with user status={current_user.status}",
                )

    return
