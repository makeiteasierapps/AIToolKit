import os
import gunicorn.app.base
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.core.MongoDbClient import MongoDbClient
from backend.middleware.auth_middleware import AuthMiddleware
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