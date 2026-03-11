"""
Pizza Social AI - FastAPI Server
The AI brain behind the Telegram → Social Media pipeline.

Endpoints:
  POST /pipeline/full      - Full pipeline: analyze → enhance → video (slow, ~5-8 min)
  POST /pipeline/analyze   - Just analyze food + generate caption/hashtags
  POST /pipeline/enhance   - Just enhance the image
  POST /pipeline/video     - Just generate a video
  POST /pending/save       - Save a pending post for approval
  GET  /pending/{post_id}  - Retrieve a pending post
  POST /post/all           - Post to all social media platforms
  GET  /health             - Health check
"""

import uuid
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from services.openai_service import analyze_food, generate_caption, generate_image_prompt
from services.falai_service import enhance_image
from services.runway_service import generate_video
from services.social_service import post_to_all

app = FastAPI(title="Pizza Social AI", version="1.0.0")

# In-memory store for posts awaiting Telegram approval
# Key: post_id (str), Value: dict with all post data
pending_posts: dict = {}


# ── Request / Response Models ──────────────────────────────────────────────────

class PhotoRequest(BaseModel):
    photo_url: str   # Public URL of the Telegram photo


class EnhanceRequest(BaseModel):
    photo_url: str
    food_description: str


class VideoRequest(BaseModel):
    image_url: str   # Use the enhanced image URL


class SavePendingRequest(BaseModel):
    caption: str
    hashtags: str
    enhanced_image_url: str
    video_url: str
    food_description: str
    chat_id: str


class PostRequest(BaseModel):
    caption: str
    hashtags: str
    enhanced_image_url: str
    video_url: str


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "Pizza Social AI"}


@app.post("/pipeline/analyze")
async def pipeline_analyze(req: PhotoRequest):
    """Analyze food photo → return description, caption, hashtags."""
    try:
        description = await analyze_food(req.photo_url)
        caption, hashtags = await generate_caption(description)
        return {
            "food_description": description,
            "caption": caption,
            "hashtags": hashtags
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pipeline/enhance")
async def pipeline_enhance(req: EnhanceRequest):
    """Enhance raw food photo using fal.ai FLUX Pro."""
    try:
        prompt = await generate_image_prompt(req.food_description)
        enhanced_url = await enhance_image(req.photo_url, prompt)
        return {"enhanced_image_url": enhanced_url, "prompt_used": prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pipeline/video")
async def pipeline_video(req: VideoRequest):
    """Generate cinematic video from image using Runway Gen-3."""
    try:
        video_url = await generate_video(req.image_url)
        return {"video_url": video_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pipeline/full")
async def pipeline_full(req: PhotoRequest):
    """
    Full pipeline in one call:
    1. Analyze food with GPT-4o Vision
    2. Generate caption + hashtags
    3. Enhance image with fal.ai FLUX Pro
    4. Generate video with Runway Gen-3
    Returns everything needed for approval.
    NOTE: This takes 5-10 minutes due to AI generation times.
    """
    try:
        # Step 1: Analyze
        description = await analyze_food(req.photo_url)
        caption, hashtags = await generate_caption(description)

        # Step 2: Enhance image
        prompt = await generate_image_prompt(description)
        enhanced_url = await enhance_image(req.photo_url, prompt)

        # Step 3: Generate video from enhanced image
        video_url = await generate_video(enhanced_url)

        return {
            "food_description": description,
            "caption": caption,
            "hashtags": hashtags,
            "enhanced_image_url": enhanced_url,
            "video_url": video_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pending/save")
async def save_pending(req: SavePendingRequest):
    """Save a processed post while waiting for Telegram approval."""
    post_id = str(uuid.uuid4())[:8]   # short ID for callback_data
    pending_posts[post_id] = req.dict()
    return {"post_id": post_id}


@app.get("/pending/{post_id}")
async def get_pending(post_id: str):
    """Retrieve a pending post by ID (called when user approves)."""
    post = pending_posts.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail=f"No pending post with id '{post_id}'")
    return post


@app.delete("/pending/{post_id}")
async def delete_pending(post_id: str):
    """Remove a pending post (called after approval or rejection)."""
    pending_posts.pop(post_id, None)
    return {"deleted": post_id}


@app.post("/post/all")
async def post_all(req: PostRequest):
    """Post to Instagram, Facebook, TikTok, and Google Business simultaneously."""
    try:
        results = await post_to_all(
            req.caption,
            req.hashtags,
            req.enhanced_image_url,
            req.video_url
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
