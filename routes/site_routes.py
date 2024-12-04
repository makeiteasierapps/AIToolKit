from datetime import datetime
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from pydantic import BaseModel, EmailStr
from typing import AsyncGenerator
import bcrypt
import logging
from starlette.authentication import requires


logger = logging.getLogger(__name__)

router = APIRouter()

class WebsiteDescription(BaseModel):
    website_description: str

class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str

async def get_user(db, username: str):
    try:
        return await db.users.find_one({"username": username})
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}", exc_info=True)
        return None

async def get_user_by_email(db, email: str):
    try:
        return await db.users.find_one({"email": email})
    except Exception as e:
        logger.error(f"Error getting user by email: {str(e)}", exc_info=True)
        return None

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "login.html", 
        {"request": request}
    )

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "signup.html", 
        {"request": request}
    )

@router.post("/signup")
async def signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    db = request.app.state.db
    
    # Check if username or email already exists
    try:
        if await get_user(db, username):
            return request.app.state.templates.TemplateResponse(
                "signup.html",
                {
                    "request": request,
                    "error": "Username already exists"
                }
            )
    
        if await get_user_by_email(db, email):
            return request.app.state.templates.TemplateResponse(
                "signup.html",
                {
                    "request": request,
                    "error": "Email already registered"
                }
            )
    except Exception as e:
        logger.error(f"Error checking for existing user: {str(e)}", exc_info=True)
        return request.app.state.templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": f"An error occurred during signup: {str(e)}"
            }
        )
    # Hash password and create user
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    new_user = {
        "username": username,
        "email": email,
        "password": hashed_password,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow()
    }
    
    try:
        await db.users.insert_one(new_user)
        request.session["authenticated"] = True
        request.session["username"] = username
        request.session["email"] = email
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        return request.app.state.templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": f"An error occurred during signup: {str(e)}"
            }
        )

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    db = request.app.state.db
    user = await get_user(db, username)
    
    try:
        if user and bcrypt.checkpw(password.encode(), user["password"]):
            # Update last login
            await db.users.update_one(
                {"username": username},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            request.session["authenticated"] = True
            request.session["username"] = username
            request.session["email"] = user["email"]
            logger.info(f"User {username} logged in")
            return RedirectResponse(url="/", status_code=303)
    
        return request.app.state.templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid username or password"
            }
            )
    except Exception as e:
        logger.error(f"Error logging in: {str(e)}", exc_info=True)
        return request.app.state.templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": f"An error occurred during login: {str(e)}"
            }
        )

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")

@router.get("/", response_class=HTMLResponse)
@requires("authenticated", redirect="login")
async def home(request: Request):
    print(request.user)
    if not request.user.is_authenticated:
        return RedirectResponse(url="/login", status_code=303)
    return request.app.state.templates.TemplateResponse("home.html", {"request": request})

@router.get("/site_builder", response_class=HTMLResponse)
async def site_builder(request: Request):
    if not request.user.is_authenticated:
        return RedirectResponse(url="/login", status_code=303)
    return request.app.state.templates.TemplateResponse("site_builder.html", {"request": request})

@router.post("/page_builder")
async def start_pipeline(request: Request, description: WebsiteDescription):
    if not request.user.is_authenticated:
        return RedirectResponse(url="/login", status_code=303)
    db = request.app.state.db
    if not description.website_description.strip():
        return StreamingResponse(
            iter(['data: {"type": "error", "message": "Please provide a website description"}\n\n']),
            media_type="text/event-stream"
        )

    async def generate() -> AsyncGenerator[str, None]:
        try:
            async for html_update in request.app.state.component_builder_pipeline(description.website_description, db):
                yield f"data: {html_update}\n\n"
        except Exception as e:
            yield f'data: {{"type": "error", "message": "Pipeline error: {str(e)}"}}\n\n'

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )
