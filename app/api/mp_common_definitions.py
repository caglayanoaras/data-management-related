from typing import Annotated

from fastapi import ( 
    APIRouter, Response, Request, Depends)
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import get_session
from app.crud.users_and_permissions import *
from app.models import User
from app.dependencies.auth import (
    get_current_active_user, 
    )

# Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

SessionDep = Annotated[Session, Depends(get_session)]

mp_common_definitions_router = APIRouter(
    prefix="/mp_common_definitions",
    responses={404: {"description": "Not found"}},
    tags=['M&P Common Definitions']
)

@mp_common_definitions_router.get("/", name='mp_common_definitions_index', include_in_schema=False, response_class=HTMLResponse)
async def mp_common_definitions_index(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return templates.TemplateResponse("mp_common_definitions.html", {
        "request": request,
        "user": current_user,
    })