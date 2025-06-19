from typing import Sequence

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.controller import register_oldboy_applicant_controller, process_oldboy_applicant_controller, reactivate_oldboy_controller
from src.db import SessionDep
from src.model import OldboyApplicant, User
from src.util import get_user


oldboy_router = APIRouter(tags=['oldboy'])


@oldboy_router.post('/oldboy/register', status_code=201)
async def create_oldboy_applicant(session: SessionDep, request: Request) -> OldboyApplicant:
    current_user = get_user(request)
    return await register_oldboy_applicant_controller(session, current_user)


@oldboy_router.get('/executive/oldboy/applicants')
async def get_oldboy_applicants(session: SessionDep, processed: bool) -> Sequence[OldboyApplicant]:
    return session.exec(select(OldboyApplicant).where(OldboyApplicant.processed == processed)).all()


@oldboy_router.post('/executive/oldboy/{id}/process', status_code=204)
async def process_oldboy_applicant(id: str, session: SessionDep) -> None:
    return await process_oldboy_applicant_controller(session, id)


@oldboy_router.post('/oldboy/unregister', status_code=204)
async def delete_oldboy_applicant_self(session: SessionDep, request: Request) -> None:
    current_user = get_user(request)
    oldboy_applicant = session.get(OldboyApplicant, current_user.id)
    if not oldboy_applicant: raise HTTPException(404, detail="oldboy_applicant not found")
    session.delete(oldboy_applicant)
    session.commit()
    return


@oldboy_router.post('/executive/oldboy/{id}/unregister', status_code=204)
async def delete_oldboy_applicant_executive(id: str, session: SessionDep) -> None:
    user = session.get(User, id)
    if not user: raise HTTPException(404, detail="user does not exist")
    oldboy_applicant = session.get(OldboyApplicant, user.id)
    if not oldboy_applicant: raise HTTPException(404, detail="oldboy_applicant not found")
    session.delete(oldboy_applicant)
    session.commit()
    return


@oldboy_router.post('/oldboy/reactivate', status_code=204)
async def reactivate_oldboy(session: SessionDep, request: Request) -> None:
    current_user = get_user(request)
    return await reactivate_oldboy_controller(session, current_user)
