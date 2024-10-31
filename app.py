from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from site_builder import page_builder_pipeline

app = FastAPI()

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

@app.post("/page_builder")
async def start_pipeline(description: WebsiteDescription):
    if not description.website_description.strip():
        return StreamingResponse(
            iter(['data: {"type": "error", "message": "Please provide a website description"}\n\n']),
            media_type="text/event-stream"
        )

    async def generate():
        try:
            for html_update in page_builder_pipeline(description.website_description):
                yield f"data: {html_update}\n\n"
        except Exception as e:
            yield f'data: {{"type": "error", "message": "Pipeline error: {str(e)}"}}\n\n'

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)