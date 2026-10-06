import os
import requests
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
IG_USER_ID = (os.getenv("IG_USER_ID") or "").strip()
IG_ACCESS_TOKEN = (os.getenv("IG_ACCESS_TOKEN") or "").strip()
PORT = int(os.getenv("PORT", 10000))
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL", "")

def extract_direct_video_url(reel_url):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(reel_url, download=False)
        return info.get('url')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot active hai! Kisi bhi Instagram Reel ka link bhejo, wo aapke account par repost ho jayegi.")

async def post_reel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reel_url = update.message.text.strip()
    if not ("instagram.com" in reel_url or reel_url.startswith("http")):
        await update.message.reply_text("Kripya valid Instagram Reel URL bhejo.")
        return

    status_msg = await update.message.reply_text("⏳ Reel extract ho rahi hai...")

    try:
        direct_video_url = extract_direct_video_url(reel_url)
        if not direct_video_url:
            await status_msg.edit_text("❌ Video URL nahi mila. Account private ho sakta hai.")
            return
    except Exception as e:
        await status_msg.edit_text(f"❌ Extraction error: {str(e)}")
        return

    await status_msg.edit_text("🚀 Instagram par Reel post ho rahi hai...")

    create_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "video_url": direct_video_url,
        "access_token": IG_ACCESS_TOKEN
    }

    res = requests.post(create_url, data=payload).json()
    if "id" not in res:
        await status_msg.edit_text(f"❌ Container error: {res}")
        return

    creation_id = res["id"]

    await status_msg.edit_text("⏳ Processing video on Instagram...")
    import asyncio
    await asyncio.sleep(15)

    publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    pub_payload = {
        "creation_id": creation_id,
        "access_token": IG_ACCESS_TOKEN
    }

    pub_res = requests.post(publish_url, data=pub_payload).json()
    if "id" in pub_res:
        await status_msg.edit_text("✅ Reel successfully post ho gayi!")
    else:
        await status_msg.edit_text(f"❌ Publish error: {pub_res}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), post_reel))

    if WEBHOOK_URL:
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TELEGRAM_BOT_TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
        )
    else:
        app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
