from fastapi import APIRouter

from .major import major_router
from .pig import pig_router
from .sig import sig_router
from .user import user_router
from .article import article_router
from .board import board_router
from .comment import comment_router, comment_executive_router
from .file import file_router
from .scsc import scsc_router
from .bot import bot_router

root_router = APIRouter()

root_router.include_router(major_router, prefix='/api')
root_router.include_router(user_router, prefix='/api')
root_router.include_router(sig_router, prefix='/api')
root_router.include_router(pig_router, prefix='/api')
root_router.include_router(article_router, prefix='/api')
root_router.include_router(comment_router, prefix='/api')
root_router.include_router(comment_executive_router, prefix='/api')
root_router.include_router(board_router, prefix='/api')
root_router.include_router(file_router, prefix='/api')
root_router.include_router(scsc_router, prefix='/api')
root_router.include_router(bot_router, prefix='/api')

