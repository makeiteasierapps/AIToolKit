from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from typing import  Annotated
from backend.config.logging_config import setup_logging
from backend.config.Oauth2 import get_current_user
from backend.models.UserModel import User

logger = setup_logging()

site_router = APIRouter()

def get_db(request: Request):
    return request.app.state.db

@site_router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)]
):

    return request.app.state.templates.TemplateResponse(
        "home.html", 
        {"request": request, "user": current_user}
    )

@site_router.get("/site_builder", response_class=HTMLResponse)
async def site_builder(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)]
):
    return request.app.state.templates.TemplateResponse(
        "site_builder.html", 
        {"request": request, "user": current_user}
    )