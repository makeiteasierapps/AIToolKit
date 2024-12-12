from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
from typing import Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from backend.config.logging_config import setup_logging
from backend.models.UserModel import User

logger = setup_logging()

load_dotenv()

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Security utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_user(db, username: str) -> User | None:
    try:
        user_dict = await db.users.find_one({"username": username})
        if user_dict:
            user_dict["user_id"] = str(user_dict["_id"])
            user_dict.pop("_id")
            return User(**user_dict)
        return None
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}", exc_info=True)
        return None

async def authenticate_user(db, username: str, password: str):
    try:
        user = await get_user(db, username)
        if not user or not verify_password(password, user.hashed_password):
            return False
        return user
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return False

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        logger.error(f"Token creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create token"
        )

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    request: Request
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.exceptions.InvalidTokenError:
        raise credentials_exception

    db = request.app.state.db
    user = await get_user(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user

def create_token_pair(user_data: dict):
    try:
        access_token = create_access_token(
            data=user_data,
            expires_delta=timedelta(seconds=10)
        )

        refresh_token = create_access_token(
            data={"sub": user_data["sub"], "type": "refresh"},
            expires_delta=timedelta(days=7)
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    except Exception as e:
        logger.error(f"Token pair creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create token pair"
        )

def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            logger.error("Invalid token type")
            raise HTTPException(status_code=400, detail="Invalid refresh token")

        new_token = create_access_token(data={"sub": payload["sub"]})
        return new_token
    except jwt.exceptions.InvalidTokenError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid refresh token")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise
