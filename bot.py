import os
import threading
import time
import requests
import yt_dlp
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
IG_USER_ID = (os.getenv("IG_USER_ID") or "").strip()
IG_ACCESS_TOKEN = (os.getenv("IG_ACCESS_TOKEN") or "").strip()

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

def run_health_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

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

    status_msg = await update.message.reply_text("⏳ Reel se video nikaali ja rahi hai...")

    try:
        direct_video_url = extract_direct_video_url(reel_url)
        if not direct_video_url:
            await status_msg.edit_text("❌ Video link nahi mil paaya. Reel private ho sakti hai.")
            return
    except Exception as e:
        await status_msg.edit_text(f"❌ Error video nikaalne mein: {str(e)}")
        return

    await status_msg.edit_text("🚀 Instagram par upload shuru ho gaya...")

    create_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "video_url": direct_video_url,
        "access_token": IG_ACCESS_TOKEN
    }

    res = requests.post(create_url, data=payload).json()
    if "id" not in res:
        await status_msg.edit_text(f"❌ Error container banane mein: {res}")
        return

    creation_id = res["id"]

    await status_msg.edit_text("⏳ Instagram video process kar raha hai, 15 second rukiye...")
    time.sleep(15)

    publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    pub_payload = {
        "creation_id": creation_id,
        "access_token": IG_ACCESS_TOKEN
    }

    pub_res = requests.post(publish_url, data=pub_payload).json()
    if "id" in pub_res:
        await status_msg.edit_text("✅ Reel aapke Instagram par successfully post ho gayi!")
    else:
        await status_msg.edit_text(f"❌ Publish error: {pub_res}")

def main():
    threading.Thread(target=run_health_server, daemon=True).start()
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), post_reel))
    app.run_polling()

if __name__ == "__main__":
    main()
    
