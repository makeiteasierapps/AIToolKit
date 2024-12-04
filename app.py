import os
import base64
import json
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from itsdangerous import URLSafeSerializer
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend, 
    AuthenticationError,
    BaseUser
)
from starlette.middleware.authentication import AuthenticationMiddleware
from fastapi.responses import RedirectResponse
from config.logging_config import setup_logging
from config.server_config import run_server
from routes.site_routes import router
from MongoDbClient import MongoDbClient
from component_builder import component_builder_pipeline
load_dotenv()
logger = setup_logging()
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY")
print(SESSION_SECRET_KEY)
# Add custom User class
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
    async def authenticate(self, conn):
        # Paths that don't require authentication
        public_paths = ["/login", "/static", "/signup"]
        if any(conn.url.path.startswith(path) for path in public_paths):
            return None

        if 'cookie' not in conn.headers:
            return
        
        # Get the session cookie
        cookie = conn.headers['cookie']
        try:
            _, session_cookie = cookie.split('=', 1)
            print(session_cookie)
        except ValueError:
            return

        try:
            decoded = base64.urlsafe_b64decode(session_cookie.split('.')[0] + '==')
            session_data = json.loads(decoded)
            print(session_data)
            if not session_data.get("authenticated"):
                return None

            username = session_data.get("username")
            if not username:
                return None

            # Return both credentials and user object
            return AuthCredentials(["authenticated"]), User(
                username=username,
                email=session_data.get("email")
            )
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise AuthenticationError('Invalid session credentials')

def on_auth_error():
    return RedirectResponse(url="/login", status_code=303)

@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("Starting up the application...")
    logger.info(f"Environment: {'Development' if os.getenv('IS_LOCAL_DEV') == 'true' else 'Production'}")
    
    # Initialize state
    mongo_client = MongoDbClient.get_instance("ai-toolkit")
    application.state.db = mongo_client.db
    application.state.templates = Jinja2Templates(directory="templates")
    application.state.component_builder_pipeline = component_builder_pipeline
    
    yield

# Create the FastAPI instance at module level
app = FastAPI(lifespan=lifespan)

# Add SessionMiddleware first
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY
)

# Add AuthenticationMiddleware with our custom backend
app.add_middleware(
    AuthenticationMiddleware,
    backend=SessionAuthBackend(),
    on_error=on_auth_error
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/mnt/media_storage/generated", StaticFiles(directory="mnt/media_storage/generated"), name="generated_media")

# Include routes
app.include_router(router)

if __name__ == "__main__":
    run_server(app)