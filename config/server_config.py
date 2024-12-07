import os
import gunicorn.app.base
import uvicorn
from fastapi import FastAPI, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.requests import Request
from fastapi.responses import RedirectResponse, JSONResponse
from MongoDbClient import MongoDbClient
from component_builder import component_builder_pipeline

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
            "app:app",
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
        if not access_token or not access_token.startswith('Bearer '):
            # If no valid token and requesting HTML page, redirect to login
            if request.headers.get('accept', '').startswith('text/html'):
                return RedirectResponse(url='/auth/login')
            
            # For API calls without token, return 401
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"}
            )
        
        # Add the token to the request headers for downstream middleware/dependencies
        request.headers.__dict__["_list"].append(
            (b'authorization', access_token.encode())
        )
            
        return await call_next(request)

class ServerConfig:
    def __init__(self, app: FastAPI):
        self.app = app

    def setup_static_files(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.app.mount("/static", StaticFiles(directory=os.path.join(project_root, "static")), name="static")
        self.app.mount(
            "/mnt/media_storage/generated",
            StaticFiles(directory="/mnt/media_storage/generated"),
            name="generated_media"
        )

    def setup_state(self):
        mongo_client = MongoDbClient.get_instance("ai-toolkit")
        self.app.state.db = mongo_client.db
        self.app.state.templates = Jinja2Templates(directory="templates")
        self.app.state.component_builder_pipeline = component_builder_pipeline

    def configure(self):
        self.app.add_middleware(AuthMiddleware)
        self.setup_static_files()
        self.setup_state()