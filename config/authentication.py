from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
import secrets
from starlette.authentication import (
    AuthCredentials, 
    AuthenticationBackend,
    AuthenticationError,
    BaseUser
)
from bson.objectid import ObjectId
import base64
import json
from typing import Optional, Tuple
from config.logging_config import setup_logging

logger = setup_logging()

class SessionManager:
    def __init__(self, db):
        self.db = db
        self.session_expiry = timedelta(hours=24)  # Configurable expiration time

    async def create_session(self, user_id: str) -> dict:
        session_id = secrets.token_urlsafe(32)
        session_data = {
            "user_id": ObjectId(user_id),
            "session_id": session_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + self.session_expiry,
            "is_valid": True
        }
        await self.db.sessions.insert_one(session_data)
        return session_data

    async def validate_session(self, session_id: str) -> Optional[dict]:
        session = await self.db.sessions.find_one({
            "session_id": session_id,
            "is_valid": True,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        return session

    async def invalidate_session(self, session_id: str) -> None:
        await self.db.sessions.update_one(
            {"session_id": session_id},
            {"$set": {"is_valid": False}}
        )

    async def invalidate_user_sessions(self, user_id: str) -> None:
        await self.db.sessions.update_many(
            {"user_id": ObjectId(user_id)},
            {"$set": {"is_valid": False}}
        )

class User(BaseUser):
    def __init__(self, username: str, email: str = None):
        self.username = username
        self.email = email

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username

    @property
    def identity(self) -> str:
        return self.username

class SessionAuthBackend(AuthenticationBackend):
    PUBLIC_PATHS = ["/login", "/static", "/signup"]
    
    async def authenticate(self, conn) -> Optional[Tuple[AuthCredentials, User]]:
        if any(conn.url.path.startswith(path) for path in self.PUBLIC_PATHS):
            return None

        session = self._get_session_data(conn)
        if not session:
            return None

        # Fetch user from database using user_id
        session_id = session.get("session_id")
        if not session_id:
            return None

        # Validate session in database
        db = conn.app.state.db
        session_manager = SessionManager(db)
        valid_session = await session_manager.validate_session(session_id)

        if not valid_session:
            return None

        # Get fresh user data from database
        user_data = await db.users.find_one({"_id": valid_session["user_id"]})
        if not user_data:
            return None
        
        return AuthCredentials(["authenticated"]), User(
            username=user_data["username"],
            email=user_data["email"]
        )

    def _get_session_data(self, conn) -> Optional[dict]:
        if 'cookie' not in conn.headers:
            return None
            
        try:
            _, session_cookie = conn.headers['cookie'].split('=', 1)
            decoded = base64.urlsafe_b64decode(session_cookie.split('.')[0] + '==')
            return json.loads(decoded)
        except Exception as e:
            logger.error(f"Session data extraction error: {str(e)}")
            return None

def on_auth_error():
    return RedirectResponse(url="/login", status_code=303)
