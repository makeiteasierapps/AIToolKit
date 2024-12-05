from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from config.Oauth2 import (
    Token, get_password_hash, 
    create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user, authenticate_user
)
from fastapi.responses import HTMLResponse

from config.logging_config import setup_logging

logger = setup_logging()
auth_routes = APIRouter(prefix="/auth", tags=["authentication"])

def get_db(request: Request):
    return request.app.state.db

@auth_routes.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "login.html", 
        {"request": request}
    )

@auth_routes.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db = Depends(get_db)
) -> Token:
    # Find user in database
    user = await authenticate_user(db, form_data.username, form_data.password)
    print(user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, 
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@auth_routes.get("/register", response_class=HTMLResponse)
async def signup_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "signup.html", 
        {"request": request}
    )

@auth_routes.post("/register")
async def register_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db = Depends(get_db)
):
    # Check if user exists
    existing_user = await db.users.find_one({"username": form_data.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(form_data.password)
    user_data = {
        "username": form_data.username,
        "hashed_password": hashed_password,
        "disabled": False
    }
    
    await db.users.insert_one(user_data)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_routes.post("/logout")
async def logout(request: Request):
    try:
        session_id = request.session.get("session_id")
        if session_id:
            pass
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(status_code=500, detail="Error during logout")
    
    request.session.clear()
    return {"status": "success"}

@auth_routes.get("/me")
async def read_users_me(
    current_user: Annotated[dict, Depends(get_current_user)]
):
    print(current_user)
    return current_user