import httpx
import asyncio
import os

FAL_API_KEY = os.getenv("FAL_API_KEY")
FAL_HEADERS = {
    "Authorization": f"Key {FAL_API_KEY}",
    "Content-Type": "application/json"
}
MODEL = "fal-ai/flux-pro/v1.1-ultra"
BASE_URL = f"https://queue.fal.run/{MODEL}"


async def enhance_image(photo_url: str, prompt: str) -> str:
    """
    Transform a raw food photo into a stunning AI-enhanced marketing image.
    Uses FLUX Pro Ultra via fal.ai queue API.
    """
    async with httpx.AsyncClient(timeout=300) as client:
        # Submit job to queue
        submit = await client.post(
            BASE_URL,
            headers=FAL_HEADERS,
            json={
                "prompt": prompt,
                "image_url": photo_url,
                "num_images": 1,
                "aspect_ratio": "1:1",
                "output_format": "jpeg",
                "safety_tolerance": "5",
                "enable_safety_checker": False
            }
        )
        submit.raise_for_status()
        job = submit.json()
        request_id = job.get("request_id")

        if not request_id:
            raise RuntimeError(f"fal.ai did not return request_id: {job}")

        # Poll for completion (up to 5 minutes)
        for _ in range(60):
            await asyncio.sleep(5)
            status_resp = await client.get(
                f"{BASE_URL}/requests/{request_id}/status",
                headers=FAL_HEADERS
            )
            status = status_resp.json()

            if status.get("status") == "COMPLETED":
                result_resp = await client.get(
                    f"{BASE_URL}/requests/{request_id}",
                    headers=FAL_HEADERS
                )
                result = result_resp.json()
                return result["images"][0]["url"]

            if status.get("status") == "FAILED":
                raise RuntimeError(f"fal.ai job failed: {status}")

        raise TimeoutError("fal.ai image enhancement timed out after 5 minutes")
