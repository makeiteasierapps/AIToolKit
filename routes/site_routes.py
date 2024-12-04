from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator
from starlette.authentication import requires
from config.logging_config import setup_logging


logger = setup_logging()

site_router = APIRouter()

class WebsiteDescription(BaseModel):
    website_description: str


@site_router.get("/", response_class=HTMLResponse)
@requires("authenticated", redirect="login")
async def home(request: Request):
    return request.app.state.templates.TemplateResponse("home.html", {"request": request})

@site_router.get("/site_builder", response_class=HTMLResponse)
@requires("authenticated", redirect="login")
async def site_builder(request: Request):
    return request.app.state.templates.TemplateResponse("site_builder.html", {"request": request})

@site_router.post("/page_builder")
@requires("authenticated", redirect="login")
async def start_pipeline(request: Request, description: WebsiteDescription):
    db = request.app.state.db
    if not description.website_description.strip():
        return StreamingResponse(
            iter(['data: {"type": "error", "message": "Please provide a website description"}\n\n']),
            media_type="text/event-stream"
        )

    async def generate() -> AsyncGenerator[str, None]:
        try:
            async for html_update in request.app.state.component_builder_pipeline(description.website_description, db):
                yield f"data: {html_update}\n\n"
        except Exception as e:
            yield f'data: {{"type": "error", "message": "Pipeline error: {str(e)}"}}\n\n'

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )
