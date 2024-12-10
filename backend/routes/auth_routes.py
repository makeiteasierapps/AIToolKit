from typing import Annotated
from pydantic import BaseModel
from fastapi.responses import Response
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from backend.config.Oauth2 import (
    get_password_hash, 
    get_current_user, authenticate_user, refresh_access_token, create_token_pair
)
from backend.models.UserModel import User
from backend.config.logging_config import setup_logging

logger = setup_logging()
auth_routes = APIRouter(prefix="/auth", tags=["authentication"])

class UserRegistration(BaseModel):
    username: str
    email: str
    password: str 

class RefreshTokenRequest(BaseModel):
    token: str

@auth_routes.get("/login")
@auth_routes.get("/register")
async def auth_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "auth.html",
        {"request": request, "error": None}
    )

@auth_routes.get("/validate")
async def validate_session(current_user: User = Depends(get_current_user)):
    return {"status": "valid", "user": current_user}

@auth_routes.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    request: Request,
):
    user = await authenticate_user(request.app.state.db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_pair = create_token_pair({"sub": user.username})
    
    # Set the access token in cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token_pair.access_token}",
        httponly=True,
        secure=True,
        samesite="strict"
    )
    
    return {
        "status": "success",
        "refresh_token": token_pair.refresh_token
    }

@auth_routes.post("/refresh")
async def refresh_token(
    request: RefreshTokenRequest,
    response: Response
):
    try:
        new_access_token = refresh_access_token(request.token)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {new_access_token}",
            httponly=True,
            secure=True,
            samesite="strict"
        )
        return {"access_token": new_access_token, "token_type": "bearer"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )

@auth_routes.post("/register")
async def register_user(
    user_data: UserRegistration,
    response: Response,
    request: Request
):
    db = request.app.state.db
    # Check if user exists
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user_data = {
        "username": user_data.username,
        "hashed_password": hashed_password,
        "disabled": False,
        "api_request_count": 0
    }
    
    await db.users.insert_one(user_data)

    token_pair = create_token_pair({"sub": user_data["username"]})
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token_pair.access_token}",
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return {"status": "success", "refresh_token": token_pair.refresh_token}

@auth_routes.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"status": "success"}

@auth_routes.get("/me")
async def read_users_me(
    current_user: Annotated[dict, Depends(get_current_user)]
):
    return current_user