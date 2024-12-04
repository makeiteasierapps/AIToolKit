from datetime import datetime
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, EmailStr
import bcrypt
from config.logging_config import setup_logging
from config.authentication import SessionManager

logger = setup_logging()

auth_router = APIRouter()

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

@auth_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "login.html", 
        {"request": request}
    )

@auth_router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "signup.html", 
        {"request": request}
    )

@auth_router.post("/signup")
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
        request.session["uid"] = str(new_user["_id"])
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        return request.app.state.templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": f"An error occurred during signup: {str(e)}"
            }
        )

@auth_router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    db = request.app.state.db
    user = await get_user(db, username)
    
    try:
        if user and bcrypt.checkpw(password.encode(), user["password"]):
            # Create new session
            session_manager = SessionManager(db)
            
            # Invalidate any existing sessions
            await session_manager.invalidate_user_sessions(str(user["_id"]))
            
            # Create new session
            session_data = await session_manager.create_session(str(user["_id"]))
            
            # Update last login
            await db.users.update_one(
                {"username": username},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            
            # Update session with new session ID
            request.session.clear()
            request.session["session_id"] = session_data["session_id"]
            request.session["authenticated"] = True
            
            logger.info(f"User {username} logged in with new session")
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

@auth_router.post("/logout")
async def logout(request: Request):
    try:
        session_id = request.session.get("session_id")
        if session_id:
            session_manager = SessionManager(request.app.state.db)
            await session_manager.invalidate_session(session_id)
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(status_code=500, detail="Error during logout")
    
    request.session.clear()
    return {"status": "success"}
