import os
import gunicorn.app.base
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from config.authentication import SessionAuthBackend, on_auth_error
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

class ServerConfig:
    def __init__(self, app: FastAPI, session_secret_key: str):
        self.app = app
        self.session_secret_key = session_secret_key

    def setup_middlewares(self):
        self.app.add_middleware(
            SessionMiddleware,
            secret_key=self.session_secret_key,
            https_only=True
        )
        self.app.add_middleware(
            AuthenticationMiddleware,
            backend=SessionAuthBackend(),
            on_error=on_auth_error
        )

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
        self.setup_middlewares()
        self.setup_static_files()
        self.setup_state()