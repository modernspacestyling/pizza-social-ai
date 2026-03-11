import httpx
import os
from typing import Tuple

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}


async def analyze_food(photo_url: str) -> str:
    """Analyze food in photo using GPT-4o Vision"""
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=HEADERS,
            json={
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "You are a professional food marketing expert for a pizza restaurant. "
                                    "Analyze this food photo and describe:\n"
                                    "1. Exactly what food item(s) are shown\n"
                                    "2. Key visual qualities: colors, textures, toppings, presentation\n"
                                    "3. The mood and feeling it evokes (e.g. cozy, indulgent, festive)\n"
                                    "4. The best marketing angle for this dish\n\n"
                                    "Be vivid and specific. This drives the entire content creation pipeline."
                                )
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": photo_url, "detail": "high"}
                            }
                        ]
                    }
                ],
                "max_tokens": 500
            }
        )
        return response.json()["choices"][0]["message"]["content"]


async def generate_caption(food_description: str) -> Tuple[str, str]:
    """Generate a viral caption and hashtags from the food description"""
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=HEADERS,
            json={
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a viral social media content creator for a pizza restaurant. "
                            "Your captions are fun, mouth-watering, urgent, and community-focused. "
                            "Always include a call-to-action: 'Order Now', 'DM us to order', or 'Call us!'. "
                            "Use emojis strategically. Max 3 sentences."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Food analysis:\n{food_description}\n\n"
                            "Return EXACTLY in this format (no extra text):\n"
                            "CAPTION: [2-3 sentences, emoji-rich, ends with CTA]\n"
                            "HASHTAGS: [25 hashtags, no spaces between them, mix popular + niche pizza/food tags]"
                        )
                    }
                ],
                "max_tokens": 400
            }
        )
        content = response.json()["choices"][0]["message"]["content"]
        caption, hashtags = "", ""
        for line in content.splitlines():
            if line.startswith("CAPTION:"):
                caption = line.replace("CAPTION:", "").strip()
            elif line.startswith("HASHTAGS:"):
                hashtags = line.replace("HASHTAGS:", "").strip()
        return caption, hashtags


async def generate_image_prompt(food_description: str) -> str:
    """Generate a fal.ai image prompt for a catchy, professional food photo"""
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=HEADERS,
            json={
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"Create a Stable Diffusion / FLUX image prompt to make this food look incredible "
                            f"for social media marketing:\n\n{food_description}\n\n"
                            "Include: professional food photography, dramatic lighting, steam or melted cheese effects, "
                            "shallow depth of field, vibrant saturated colors, dark moody restaurant background, "
                            "macro close-up details. Keep it under 80 words. Start with the food item name."
                        )
                    }
                ],
                "max_tokens": 150
            }
        )
        return response.json()["choices"][0]["message"]["content"]
