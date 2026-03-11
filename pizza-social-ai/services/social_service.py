import httpx
import asyncio
import os
from typing import Dict, Any

# ── Credentials (loaded from .env) ───────────────────────────────────────────
META_ACCESS_TOKEN     = os.getenv("META_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID  = os.getenv("INSTAGRAM_ACCOUNT_ID")
FACEBOOK_PAGE_ID      = os.getenv("FACEBOOK_PAGE_ID")
TIKTOK_ACCESS_TOKEN   = os.getenv("TIKTOK_ACCESS_TOKEN")
GOOGLE_ACCESS_TOKEN   = os.getenv("GOOGLE_ACCESS_TOKEN")
GOOGLE_LOCATION_ID    = os.getenv("GOOGLE_LOCATION_ID")   # e.g. "accounts/123/locations/456"
SHOP_URL              = os.getenv("PIZZA_SHOP_URL", "https://yourpizzashop.com")

GRAPH = "https://graph.facebook.com/v19.0"


# ── Individual platform posters ───────────────────────────────────────────────

async def post_to_instagram(image_url: str, caption: str) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        # Step 1 – create media container
        r1 = await client.post(
            f"{GRAPH}/{INSTAGRAM_ACCOUNT_ID}/media",
            params={
                "image_url": image_url,
                "caption": caption,
                "access_token": META_ACCESS_TOKEN
            }
        )
        data1 = r1.json()
        container_id = data1.get("id")
        if not container_id:
            return {"platform": "instagram", "status": "failed", "error": data1}

        await asyncio.sleep(5)   # let container process

        # Step 2 – publish
        r2 = await client.post(
            f"{GRAPH}/{INSTAGRAM_ACCOUNT_ID}/media_publish",
            params={
                "creation_id": container_id,
                "access_token": META_ACCESS_TOKEN
            }
        )
        data2 = r2.json()
        if "id" in data2:
            return {"platform": "instagram", "status": "success", "post_id": data2["id"]}
        return {"platform": "instagram", "status": "failed", "error": data2}


async def post_to_facebook(image_url: str, caption: str) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            f"{GRAPH}/{FACEBOOK_PAGE_ID}/photos",
            params={
                "url": image_url,
                "caption": caption,
                "access_token": META_ACCESS_TOKEN
            }
        )
        data = r.json()
        if "id" in data:
            return {"platform": "facebook", "status": "success", "post_id": data["id"]}
        return {"platform": "facebook", "status": "failed", "error": data}


async def post_to_tiktok(video_url: str, caption: str) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            "https://open.tiktokapis.com/v2/post/publish/video/init/",
            headers={
                "Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "post_info": {
                    "title": caption[:150],
                    "privacy_level": "PUBLIC_TO_EVERYONE",
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False,
                    "video_cover_timestamp_ms": 1000
                },
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "video_url": video_url
                }
            }
        )
        data = r.json()
        publish_id = data.get("data", {}).get("publish_id")
        if publish_id:
            return {"platform": "tiktok", "status": "success", "publish_id": publish_id}
        return {"platform": "tiktok", "status": "failed", "error": data}


async def post_to_google_business(image_url: str, caption: str) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            f"https://mybusiness.googleapis.com/v4/{GOOGLE_LOCATION_ID}/localPosts",
            headers={
                "Authorization": f"Bearer {GOOGLE_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "languageCode": "en-US",
                "summary": caption[:1500],
                "callToAction": {
                    "actionType": "ORDER",
                    "url": SHOP_URL
                },
                "media": [{"mediaFormat": "PHOTO", "sourceUrl": image_url}],
                "topicType": "STANDARD"
            }
        )
        data = r.json()
        if "name" in data:
            return {"platform": "google_business", "status": "success", "post_name": data["name"]}
        return {"platform": "google_business", "status": "failed", "error": data}


# ── Master poster ─────────────────────────────────────────────────────────────

async def post_to_all(
    caption: str,
    hashtags: str,
    image_url: str,
    video_url: str
) -> Dict[str, Any]:
    """Post to Instagram, Facebook, TikTok, and Google Business simultaneously."""
    full_caption = f"{caption}\n\n{hashtags}"

    results = await asyncio.gather(
        post_to_instagram(image_url, full_caption),
        post_to_facebook(image_url, full_caption),
        post_to_tiktok(video_url, full_caption),
        post_to_google_business(image_url, caption),
        return_exceptions=True
    )

    def safe(r):
        return r if not isinstance(r, Exception) else {"status": "error", "error": str(r)}

    return {
        "instagram":       safe(results[0]),
        "facebook":        safe(results[1]),
        "tiktok":          safe(results[2]),
        "google_business": safe(results[3])
    }
