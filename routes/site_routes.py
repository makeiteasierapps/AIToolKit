from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator, Annotated
from config.logging_config import setup_logging
from config.Oauth2 import get_current_user
from fastapi.responses import RedirectResponse


logger = setup_logging()

site_router = APIRouter()

class WebsiteDescription(BaseModel):
    website_description: str

def get_db(request: Request):
    return request.app.state.db

@site_router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    current_user: Annotated[dict, Depends(get_current_user)] = None
):
    if not current_user:
        return RedirectResponse(url="/auth/login")
    
    return request.app.state.templates.TemplateResponse(
        "home.html", 
        {"request": request, "user": current_user}
    )

@site_router.get("/site_builder", response_class=HTMLResponse)
async def site_builder(
    request: Request,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    return request.app.state.templates.TemplateResponse(
        "site_builder.html", 
        {"request": request, "user": current_user}
    )

@site_router.post("/page_builder")
async def start_pipeline(
    request: Request,
    description: WebsiteDescription,
    current_user: Annotated[dict, Depends(get_current_user)]
):
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
