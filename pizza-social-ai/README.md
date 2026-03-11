# 🍕 Pizza Social AI — Automated Social Media Pipeline

Send a food photo from your phone → AI creates caption, enhanced image & video → You approve in Telegram → Auto-posts to Instagram, Facebook, TikTok, Google Business.

---

## Full Pipeline

```
📱 Phone Photo
      ↓ (Telegram)
🔍 GPT-4o Vision analyzes food
      ↓
✍️ GPT-4o writes caption + hashtags
      ↓
🎨 fal.ai FLUX Pro enhances photo → stunning marketing image
      ↓
🎬 Runway Gen-3 creates 5-sec cinematic video
      ↓
📨 You receive everything in Telegram for review
      ↓ (Approve / Reject buttons)
🚀 Auto-posts to: Instagram · Facebook · TikTok · Google Business
```

---

## File Structure

```
pizza-social-ai/
├── server.py                        # FastAPI server (AI brain)
├── services/
│   ├── openai_service.py            # Food analysis + caption generation
│   ├── falai_service.py             # fal.ai image enhancement
│   ├── runway_service.py            # Runway video generation
│   └── social_service.py           # Instagram/Facebook/TikTok/Google posting
├── n8n_workflow_1_pipeline.json     # n8n: Telegram photo → AI → approval
├── n8n_workflow_2_approval.json     # n8n: Approve/reject → post
├── requirements.txt
├── .env.example                     # Copy to .env and fill in your keys
└── README.md
```

---

## Setup

### 1. Install Python dependencies
```bash
cd pizza-social-ai
pip install -r requirements.txt
```

### 2. Configure environment variables
```bash
cp .env.example .env
# Edit .env and fill in ALL your API keys
```

### 3. Start the FastAPI server
```bash
python server.py
# Runs at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### 4. Import n8n workflows
1. Open your n8n instance: https://n8n.srv939860.hstgr.cloud
2. Click **"+"** → **"Import from file"**
3. Import `n8n_workflow_1_pipeline.json`
4. Import `n8n_workflow_2_approval.json`
5. In both workflows, click on each Telegram node and set your **Telegram Bot** credential
6. Activate both workflows

### 5. Configure Telegram credentials in n8n
- Go to **Settings → Credentials → New**
- Select **Telegram API**
- Paste your bot token from @BotFather

---

## API Keys — Where to Get Them

| Service | Where to get |
|---------|-------------|
| OpenAI | https://platform.openai.com/api-keys |
| fal.ai | https://fal.ai/dashboard/keys |
| Runway | https://app.runwayml.com/settings |
| Telegram Bot | Message @BotFather on Telegram |
| Meta (IG+FB) | https://developers.facebook.com |
| TikTok | https://developers.tiktok.com |
| Google Business | Google Cloud Console → OAuth 2.0 |

---

## How to Use (Daily Workflow)

1. **Take a photo** of your pizza/food
2. **Send it to your Telegram bot**
3. Wait ~5-8 minutes (AI is working)
4. **You receive in Telegram:**
   - The AI-enhanced marketing photo
   - Cinematic video link
   - Caption + hashtags preview
5. **Tap ✅ Approve** → instantly posts to all 4 platforms
6. **Tap ❌ Reject** → discarded, try again with a different photo

---

## Notes

- The Python server (`server.py`) must be running at all times (or use a process manager like `pm2` or `supervisord`)
- If your n8n is on a remote server, update `http://localhost:8000` in the HTTP Request nodes to your server's IP
- Meta requires a Facebook Page + connected Instagram Business account
- TikTok API requires a TikTok for Business developer app
- Google Business OAuth token expires — you'll need to refresh it periodically
