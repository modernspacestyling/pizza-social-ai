"""
Blotato social posting service.

Blotato API docs: https://help.blotato.com/api/start
Auth header: blotato-api-key: YOUR_KEY
Base URL: https://backend.blotato.com/v2

Flow:
  1. GET /users/me/accounts  → find accountId per platform
  2. POST /posts             → publish immediately
"""

import httpx
import os
from typing import Dict, Any, Optional

BLOTATO_API_KEY = os.getenv("BLOTATO_API_KEY")
BLOTATO_BASE = "https://backend.blotato.com/v2"
HEADERS = {
    "blotato-api-key": BLOTATO_API_KEY or "",
    "Content-Type": "application/json",
}

# Account IDs from your Blotato connected accounts.
# Run GET /accounts in this app to find these after connecting in Blotato.
INSTAGRAM_ACCOUNT_ID = os.getenv("BLOTATO_INSTAGRAM_ACCOUNT_ID")
FACEBOOK_ACCOUNT_ID  = os.getenv("BLOTATO_FACEBOOK_ACCOUNT_ID")
FACEBOOK_PAGE_ID     = os.getenv("BLOTATO_FACEBOOK_PAGE_ID")   # required for FB pages
TIKTOK_ACCOUNT_ID    = os.getenv("BLOTATO_TIKTOK_ACCOUNT_ID")
GOOGLE_ACCOUNT_ID    = os.getenv("BLOTATO_GOOGLE_ACCOUNT_ID")


async def list_accounts() -> list:
    """Return all Blotato connected accounts — use this to find account IDs."""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{BLOTATO_BASE}/users/me/accounts", headers=HEADERS)
        r.raise_for_status()
        return r.json()


async def _publish(
    account_id: str,
    platform: str,
    text: str,
    media_urls: list,
    page_id: Optional[str] = None,
) -> dict:
    """Publish a single post to one platform via Blotato."""
    target: dict = {"targetType": platform}
    if page_id:
        target["pageId"] = page_id

    payload = {
        "post": {
            "accountId": account_id,
            "content": {
                "text": text,
                "mediaUrls": media_urls,
                "platform": platform,
            },
            "target": target,
        }
    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{BLOTATO_BASE}/posts", headers=HEADERS, json=payload)
        return r.json()


async def post_to_all(
    caption: str,
    hashtags: str,
    image_url: str,
    video_url: str,
) -> Dict[str, Any]:
    """
    Post to Instagram, Facebook, TikTok, and Google Business via Blotato.

    - Instagram / Google Business → enhanced image
    - Facebook                    → enhanced image (page_id required for pages)
    - TikTok                      → video
    """
    full_text = f"{caption}\n\n{hashtags}"
    results: Dict[str, Any] = {}

    # ── Instagram ──────────────────────────────────────────────────────────────
    if INSTAGRAM_ACCOUNT_ID:
        results["instagram"] = await _publish(
            account_id=INSTAGRAM_ACCOUNT_ID,
            platform="instagram",
            text=full_text,
            media_urls=[image_url],
        )
    else:
        results["instagram"] = {"skipped": "BLOTATO_INSTAGRAM_ACCOUNT_ID not set"}

    # ── Facebook ───────────────────────────────────────────────────────────────
    if FACEBOOK_ACCOUNT_ID:
        results["facebook"] = await _publish(
            account_id=FACEBOOK_ACCOUNT_ID,
            platform="facebook",
            text=full_text,
            media_urls=[image_url],
            page_id=FACEBOOK_PAGE_ID or None,
        )
    else:
        results["facebook"] = {"skipped": "BLOTATO_FACEBOOK_ACCOUNT_ID not set"}

    # ── TikTok ─────────────────────────────────────────────────────────────────
    if TIKTOK_ACCOUNT_ID:
        results["tiktok"] = await _publish(
            account_id=TIKTOK_ACCOUNT_ID,
            platform="tiktok",
            text=full_text,
            media_urls=[video_url],
        )
    else:
        results["tiktok"] = {"skipped": "BLOTATO_TIKTOK_ACCOUNT_ID not set"}

    # ── Google Business ────────────────────────────────────────────────────────
    if GOOGLE_ACCOUNT_ID:
        results["google_business"] = await _publish(
            account_id=GOOGLE_ACCOUNT_ID,
            platform="googlebusiness",
            text=full_text,
            media_urls=[image_url],
        )
    else:
        results["google_business"] = {"skipped": "BLOTATO_GOOGLE_ACCOUNT_ID not set"}

    return results
