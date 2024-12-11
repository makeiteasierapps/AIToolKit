import os
import gunicorn.app.base
import uvicorn
from fastapi import FastAPI, status, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.requests import Request
from fastapi.responses import RedirectResponse, JSONResponse
from backend.core.MongoDbClient import MongoDbClient
from backend.config.Oauth2 import (refresh_access_token)
from backend.config.logging_config import setup_logging

logger = setup_logging()

def get_server_config():
    return {
        "bind": "0.0.0.0:8000",
        "worker_class": "uvicorn.workers.UvicornWorker",
        "workers": 4,
        "timeout": 600,
        "loglevel": "info",
    }

class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

def run_server(app):
    IS_LOCAL_DEV = os.getenv("IS_LOCAL_DEV", "false") == "true"

    if IS_LOCAL_DEV:
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
    else:
        StandaloneApplication(app, get_server_config()).run()

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_paths = ['/auth/login', '/auth/register', '/auth/token', 
                       '/static/', '/favicon.ico', '/auth/refresh']
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        # Check for token in cookies
        access_token = request.cookies.get('access_token')
        refresh_token = request.cookies.get('refresh_token')
        if not access_token or not access_token.startswith('Bearer '):
            if refresh_token and request.headers.get('accept', '').startswith('text/html'):
                try:
                    # Attempt to refresh the token
                    new_token = refresh_access_token(refresh_token)
                    response = RedirectResponse(
                        url=request.url.path,  # Redirect to the same page
                        status_code=status.HTTP_302_FOUND
                    )
                    response.set_cookie(
                        key="access_token",
                        value=f"Bearer {new_token}",
                        httponly=True,
                        secure=True,
                        samesite="lax"
                    )
                    return response
                except Exception:
                    # If refresh fails, redirect to login
                    return RedirectResponse(url='/auth/login')
            
            # If no refresh token or not HTML request
            if request.headers.get('accept', '').startswith('text/html'):
                return RedirectResponse(url='/auth/login')
            
            # For API calls without token, return 401
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"}
            )
        
        try:
            # Add the token to the request headers for downstream middleware/dependencies
            request.headers.__dict__["_list"].append(
                (b'authorization', access_token.encode())
            )
            
            # Attempt to process the request
            response = await call_next(request)
            
            if response.status_code == status.HTTP_401_UNAUTHORIZED and refresh_token:
                try:
                    new_token = refresh_access_token(refresh_token)
                    response = RedirectResponse(
                        url=request.url.path,
                        status_code=status.HTTP_302_FOUND
                    )
                    response.set_cookie(
                        key="access_token",
                        value=f"Bearer {new_token}",
                        httponly=True,
                        secure=True,
                        samesite="lax"
                    )
                    return response
                except Exception as e:
                    logger.error(f"Error refreshing token: {str(e)}")
                    if request.headers.get('accept', '').startswith('text/html'):
                        return RedirectResponse(url='/auth/login')
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Not authenticated"}
                    )
            
            return response
            
        except HTTPException as e:
            # Handle other exceptions
            raise e

class ServerConfig:
    def __init__(self, app: FastAPI):
        self.app = app

    def setup_static_files(self):
        # Get the project root (one level up from backend folder)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        IS_LOCAL_DEV = os.getenv("IS_LOCAL_DEV", "false") == "true"

        # Mount static files directory
        static_dir = os.path.join(project_root, "static")
        self.app.mount("/static", StaticFiles(directory=static_dir), name="static")

        # Set media storage path based on environment
        if IS_LOCAL_DEV:
            media_path = os.path.join(project_root, "mnt", "media_storage", "generated")
        else:
            media_path = "/mnt/media_storage/generated"

        # Mount media directory
        self.app.mount(
            "/mnt/media_storage/generated",
            StaticFiles(directory=media_path),
            name="generated_media"
        )

    def setup_state(self):
        mongo_client = MongoDbClient.get_instance("ai-toolkit")
        self.app.state.db = mongo_client.db
        self.app.state.templates = Jinja2Templates(directory="templates")

    def configure(self):
        self.app.add_middleware(AuthMiddleware)
        self.setup_static_files()
        self.setup_state()