import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.logging_config import setup_logging
from config.server_config import ServerConfig, run_server
from routes.site_routes import site_router
from routes.auth_routes import auth_routes

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

if __name__ == "__main__":
    run_server(app)