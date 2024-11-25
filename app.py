import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from config.logging_config import setup_logging
from config.server_config import run_server
from routes.site_routes import router
from MongoDbClient import MongoDbClient
from component_builder import component_builder_pipeline

logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the application...")
    logger.info(f"Environment: {'Development' if os.getenv('IS_LOCAL_DEV') == 'true' else 'Production'}")
    
    # Initialize state
    mongo_client = MongoDbClient.get_instance("media")
    app.state.db = mongo_client.db
    app.state.templates = Jinja2Templates(directory="templates")
    app.state.component_builder_pipeline = component_builder_pipeline
    
    yield

# Create the FastAPI instance at module level
app = FastAPI(lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/mnt/media_storage/generated", StaticFiles(directory="mnt/media_storage/generated"), name="generated_media")
# Include routes
app.include_router(router)

if __name__ == "__main__":
    load_dotenv()
    run_server(app)