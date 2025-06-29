from typing import Annotated

from fastapi import ( 
    APIRouter, Response, Request, Depends)
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import get_session
from app.crud.users_and_permissions import *
from app.models import User, UserInDB, Module
from app.dependencies.auth import (
    get_current_active_user, 
    )

# Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

SessionDep = Annotated[Session, Depends(get_session)]

design_test_catalogue_router = APIRouter(
    prefix="/design_test_catalogue",
    responses={404: {"description": "Not found"}},
    tags=['Design Test Catalogue']
)

@design_test_catalogue_router.get("/", name='design_test_catalogue_index', include_in_schema=False, response_class=HTMLResponse)
async def design_test_catalogue_index(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return templates.TemplateResponse("design_test_catalogue.html", {
        "request": request,
        "user": current_user,
    })