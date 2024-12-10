import os
from contextlib import asynccontextmanager
from fastapi import FastAPI 
from backend.config.logging_config import setup_logging
from backend.config.server_config import ServerConfig, run_server
from backend.routes.site_routes import site_router
from backend.routes.auth_routes import auth_routes
from backend.routes.page_builder_routes import page_builder_router

logger = setup_logging()

@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("Starting up the application...")
    logger.info(f"Environment: {'Development' if os.getenv('IS_LOCAL_DEV') == 'true' else 'Production'}")
    yield

app = FastAPI(lifespan=lifespan)

# Configure server
server_config = ServerConfig(app)
server_config.configure()

# Include routes
app.include_router(site_router)
app.include_router(auth_routes)
app.include_router(page_builder_router)

if __name__ == "__main__":
    run_server(app)