import os
import gunicorn.app.base
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
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
        # Skip auth check for these paths
        public_paths = ['/auth/login', '/auth/register', '/auth/token', 
                       '/static/', '/favicon.ico']
        
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        # Check for token in header
        auth_header = request.headers.get('Authorization')
        
        # If no token and requesting HTML page, redirect to login
        if not auth_header and request.headers.get('accept', '').startswith('text/html'):
            return RedirectResponse(url='/auth/login')
            
        # Otherwise, proceed with request (API calls will get 401 as needed)
        return await call_next(request)

class ServerConfig:
    def __init__(self, app: FastAPI):
        self.app = app

    def setup_static_files(self):
        self.app.mount("/static", StaticFiles(directory="static"), name="static")
        self.app.mount(
            "/mnt/media_storage/generated", 
            StaticFiles(directory="mnt/media_storage/generated"), 
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