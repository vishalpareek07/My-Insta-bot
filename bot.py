import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot active hai! Video URL bhejo Instagram reel post karne ke liye.")

async def post_reel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_url = update.message.text.strip()
    if not (video_url.startswith("http://") or video_url.startswith("https://")):
        await update.message.reply_text("Kripya valid video URL bhejo.")
        return

    status_msg = await update.message.reply_text("Reel create ho rahi hai...")

    create_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "access_token": IG_ACCESS_TOKEN
    }

    res = requests.post(create_url, data=payload).json()
    if "id" not in res:
        await status_msg.edit_text(f"Error aaya container banane mein: {res}")
        return

    creation_id = res["id"]
    publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    pub_payload = {
        "creation_id": creation_id,
        "access_token": IG_ACCESS_TOKEN
    }

    pub_res = requests.post(publish_url, data=pub_payload).json()
    if "id" in pub_res:
        await status_msg.edit_text("Reel successfully publish ho gayi!")
    else:
        await status_msg.edit_text(f"Publish error: {pub_res}")

def main():
    threading.Thread(target=run_health_server, daemon=True).start()
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), post_reel))
    app.run_polling()

if __name__ == "__main__":
    main()
    
