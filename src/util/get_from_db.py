from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import select

from src.db import DBSessionFactory, SessionDep
from src.model import SCSCGlobalStatus, UserRole


@lru_cache
def get_user_role_level(role_name: str) -> int:
    """
    Retrieves the numerical level for a given role name from the database.
    Raises ValueError if the role name does not exist.

    Args:
        role_name (str): The name of the role to look up.

    Returns:
        int: The level associated with the role.

    Raises:
        HTTPException: 400 if a role with the given name is not found in the database.
    """
    session = None
    try:
        session = DBSessionFactory().make_session()
        user_role = session.scalars(
            select(UserRole).where(UserRole.name == role_name)
        ).first()
        if not user_role:
            raise HTTPException(400, f"Role '{role_name}' not found in the database.")
        return user_role.level

    finally:
        if session:
            session.close()
