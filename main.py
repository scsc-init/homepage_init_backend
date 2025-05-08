from fastapi import FastAPI

from src.routes.major import major_router

app = FastAPI()

app.include_router(major_router, prefix='/api')