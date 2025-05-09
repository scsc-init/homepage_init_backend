from fastapi import APIRouter

from ..routes.major import major_router
from ..routes.user import user_router


root_router = APIRouter()

root_router.include_router(major_router, prefix='/api')
root_router.include_router(user_router, prefix='/api')