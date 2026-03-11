import httpx
import os
from typing import Dict, Any

PUBLER_API_KEY = os.getenv("PUBLER_API_KEY")
PUBLER_BASE = "https://api.publer.io/v1"
HEADERS = {
    "Authorization": f"Bearer {PUBLER_API_KEY}",
    "Content-Type": "application/json"
}

# Profile IDs from your Publer connected accounts
# Run GET /profiles in the app to find these
INSTAGRAM_PROFILE_ID  = os.getenv("PUBLER_INSTAGRAM_ID")
FACEBOOK_PROFILE_ID   = os.getenv("PUBLER_FACEBOOK_ID")
TIKTOK_PROFILE_ID     = os.getenv("PUBLER_TIKTOK_ID")
GOOGLE_PROFILE_ID     = os.getenv("PUBLER_GOOGLE_ID")


async def list_profiles() -> list:
    """Return all Publer connected profiles (use this to find profile IDs)."""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{PUBLER_BASE}/profiles", headers=HEADERS)
        r.raise_for_status()
        return r.json()


async def _publish(profile_ids: list, text: str, media_urls: list) -> dict:
    """Create and immediately publish a post via Publer."""
    async with httpx.AsyncClient(timeout=60) as client:
        payload = {
            "profile_ids": profile_ids,
            "text": text,
            "media_urls": media_urls,
            "publish_at": None   # None = publish immediately
        }
        r = await client.post(f"{PUBLER_BASE}/posts", headers=HEADERS, json=payload)
        return r.json()


async def post_to_all(
    caption: str,
    hashtags: str,
    image_url: str,
    video_url: str
) -> Dict[str, Any]:
    """Post to Instagram, Facebook, TikTok, and Google Business via Publer."""
    full_caption = f"{caption}\n\n{hashtags}"

    # Collect all active profile IDs
    profile_ids = [
        pid for pid in [
            INSTAGRAM_PROFILE_ID,
            FACEBOOK_PROFILE_ID,
            TIKTOK_PROFILE_ID,
            GOOGLE_PROFILE_ID,
        ] if pid
    ]

    if not profile_ids:
        return {"status": "error", "error": "No Publer profile IDs configured in .env"}

    # TikTok needs video; others get the enhanced image
    # Post image to Instagram / Facebook / Google
    image_profile_ids = [p for p in [INSTAGRAM_PROFILE_ID, FACEBOOK_PROFILE_ID, GOOGLE_PROFILE_ID] if p]
    video_profile_ids = [p for p in [TIKTOK_PROFILE_ID] if p]

    results = {}

    if image_profile_ids:
        img_result = await _publish(image_profile_ids, full_caption, [image_url])
        results["image_post"] = img_result

    if video_profile_ids:
        vid_result = await _publish(video_profile_ids, full_caption, [video_url])
        results["video_post"] = vid_result

    return results
