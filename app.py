import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from site_builder import page_builder_pipeline
from component_builder import component_builder_pipeline, test_component_builder

# Configure logging only for our application modules
logging.basicConfig(
    level=logging.INFO,  # Default level
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Set specific level for our application loggers
app_logger = logging.getLogger('app')  # Root logger for our application
app_logger.setLevel(logging.DEBUG if os.getenv("IS_LOCAL_DEV", "false") == "true" else logging.INFO)

# Set higher level for third-party libraries
logging.getLogger('uvicorn').setLevel(logging.WARNING)
logging.getLogger('fastapi').setLevel(logging.WARNING)
logging.getLogger('LiteLLM').setLevel(logging.WARNING)

logger = logging.getLogger('app.main') 

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the application...")
    logger.info(f"Environment: {'Development' if os.getenv('IS_LOCAL_DEV') == 'true' else 'Production'}")
    yield

app = FastAPI(lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class WebsiteDescription(BaseModel):
    website_description: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/site_builder", response_class=HTMLResponse)
async def site_builder(request: Request):
    return templates.TemplateResponse("site_builder.html", {"request": request})

@app.post("/component_builder", )
async def component_builder(description: WebsiteDescription):
    try:
        result = test_component_builder(description.website_description)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# @app.post("/page_builder")
# async def start_pipeline(description: WebsiteDescription):
#     if not description.website_description.strip():
#         return StreamingResponse(
#             iter(['data: {"type": "error", "message": "Please provide a website description"}\n\n']),
#             media_type="text/event-stream"
#         )

#     async def generate():
#         try:
#             for html_update in component_builder_pipeline(description.website_description):
#                 yield f"data: {html_update}\n\n"
#         except Exception as e:
#             yield f'data: {{"type": "error", "message": "Pipeline error: {str(e)}"}}\n\n'

#     return StreamingResponse(
#         generate(),
#         media_type="text/event-stream",
#         headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
#     )

if __name__ == "__main__":
    load_dotenv()
    IS_LOCAL_DEV = os.getenv("IS_LOCAL_DEV", "false") == "true"

    if IS_LOCAL_DEV:
        import uvicorn
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
    else:
        import gunicorn.app.base

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

        options = {
            "bind": "0.0.0.0:8000",
            "worker_class": "uvicorn.workers.UvicornWorker",
            "workers": 4,
            "timeout": 600,
            "loglevel": "info",
        }

        StandaloneApplication(app, options).run()