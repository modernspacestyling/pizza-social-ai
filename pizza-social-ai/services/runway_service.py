import httpx
import asyncio
import os

RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY")
RUNWAY_HEADERS = {
    "Authorization": f"Bearer {RUNWAY_API_KEY}",
    "Content-Type": "application/json",
    "X-Runway-Version": "2024-11-06"
}
BASE_URL = "https://api.dev.runwayml.com/v1"

VIDEO_PROMPT = (
    "Slow cinematic zoom in, golden melting cheese stretching, "
    "steam wisps rising, dramatic restaurant lighting, "
    "mouth-watering food advertisement style, 4K quality"
)


async def generate_video(image_url: str) -> str:
    """
    Generate a 5-second cinematic food video from an image using Runway Gen-3 Turbo.
    Returns the URL of the generated video.
    """
    async with httpx.AsyncClient(timeout=600) as client:
        # Create generation task
        create = await client.post(
            f"{BASE_URL}/image_to_video",
            headers=RUNWAY_HEADERS,
            json={
                "model": "gen3a_turbo",
                "promptImage": image_url,
                "promptText": VIDEO_PROMPT,
                "duration": 5,
                "ratio": "1280:768",
                "watermark": False
            }
        )
        create.raise_for_status()
        task = create.json()
        task_id = task.get("id")

        if not task_id:
            raise RuntimeError(f"Runway did not return task id: {task}")

        # Poll until complete (up to 10 minutes)
        for _ in range(120):
            await asyncio.sleep(5)
            poll = await client.get(
                f"{BASE_URL}/tasks/{task_id}",
                headers=RUNWAY_HEADERS
            )
            result = poll.json()
            status = result.get("status")

            if status == "SUCCEEDED":
                return result["output"][0]

            if status == "FAILED":
                raise RuntimeError(f"Runway task failed: {result.get('failure', result)}")

        raise TimeoutError("Runway video generation timed out after 10 minutes")
