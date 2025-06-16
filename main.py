"""/main.py"""

# Dependency
from fastapi import FastAPI
# Middleware
from src.middleware import APISecretMiddleware, AssertPermissionMiddleware, UserAuthMiddleware
# Route
from src.routes import root_router

app = FastAPI()

app.add_middleware(AssertPermissionMiddleware)
app.add_middleware(UserAuthMiddleware)
app.add_middleware(APISecretMiddleware)

app.include_router(root_router)
