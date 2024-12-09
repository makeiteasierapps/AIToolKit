import asyncio
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Annotated
from UserModel import User
from config.logging_config import setup_logging
from bson import ObjectId
from datetime import datetime, timezone
from config.Oauth2 import get_current_user
from component_builder import component_builder_pipeline
logger = setup_logging()

class WebsiteDescription(BaseModel):
    website_description: str

MAX_API_REQUESTS = 10

page_builder_router = APIRouter()

def get_db(request: Request):
    return request.app.state.db

@page_builder_router.get("/api/thumbnails")
async def get_thumbnails(user: User = Depends(get_current_user), db = Depends(get_db)):
    thumbnails = await db.thumbnails.find({"user_id": user.user_id}).to_list(length=None)
    return [{**t, "_id": str(t["_id"])} for t in thumbnails]

@page_builder_router.post("/api/thumbnails")
async def save_thumbnail(
    thumbnail_data: dict,
    user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    new_thumbnail = {
        "_id": ObjectId(thumbnail_data["id"]),
        "title": thumbnail_data["title"],
        "html": thumbnail_data["html"],
        "user_id": user.user_id,
        "created_at": datetime.now(timezone.utc)
    }
    await db.thumbnails.insert_one(new_thumbnail)
    new_thumbnail["_id"] = str(new_thumbnail["_id"])
    return new_thumbnail

@page_builder_router.delete("/api/thumbnails/{thumbnail_id}")
async def delete_thumbnail(
    thumbnail_id: str,
    user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    result = await db.thumbnails.delete_one({
        "_id": ObjectId(thumbnail_id),
        "user_id": user.user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    return {"message": "Thumbnail deleted"}

@page_builder_router.post("/api/requests")
async def handle_request(
    user: User = Depends(get_current_user), 
    db = Depends(get_db)
):
    user_stats = await db.users.find_one({"_id": ObjectId(user.user_id)})
    current_count = user_stats["api_request_count"] if user_stats else 0
    
    if current_count >= MAX_API_REQUESTS:
        raise HTTPException(
            status_code=403,
            detail="You have reached your API request limit"
        )
    
    await db.users.update_one(
        {"_id": ObjectId(user.user_id)},
        {
            "$inc": {"api_request_count": 1},
            "$setOnInsert": {"created_at": datetime.now(timezone.utc)}
        },
        upsert=True
    )
    
    return {
        "count": current_count + 1,
        "remaining": MAX_API_REQUESTS - (current_count + 1)
    }

@page_builder_router.post("/page_builder")
async def start_pipeline(
    request: Request,
    description: WebsiteDescription,
    current_user: Annotated[User, Depends(get_current_user)]
):
    db = request.app.state.db
    
    # Validate input
    if not description.website_description.strip():
        return JSONResponse(
            status_code=400,
            content={"message": "Please provide a website description"}
        )

    # Check API request limit
    user_stats = await db.users.find_one({"_id": ObjectId(current_user.user_id)})
    current_count = user_stats["api_request_count"] if user_stats else 0
    
    if current_count >= MAX_API_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={
                "message": "You have reached your API request limit",
                "remaining_requests": 0,
                "max_requests": MAX_API_REQUESTS
            }
        )
    
    # Increment the request count
    await db.users.update_one(
        {"_id": ObjectId(current_user.user_id)},
        {
            "$inc": {"api_request_count": 1},
            "$setOnInsert": {"created_at": datetime.now(timezone.utc)}
        },
        upsert=True
    )

    async def generate():
        try:
            # Process the actual page building
            async for html_update in component_builder_pipeline(description.website_description, db):
                if not html_update.startswith('data: '):
                    html_update = f'data: {html_update}'
                yield f"{html_update}\n\n"
                # Add a small delay to prevent buffering issues
                await asyncio.sleep(0.1)
        except Exception as e:
            yield f'data: {{"type": "error", "message": "Pipeline error: {str(e)}"}}\n\n'

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )