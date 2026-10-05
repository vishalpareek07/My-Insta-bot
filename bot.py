import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8975456161:AAHSNLlTEZ-JT45AEi_El1KQzOKNWXw_4E0"

def process_reel(url):
    cmd_dl = ["yt-dlp", "--format", "mp4", "-o", "reel.mp4", url]
    subprocess.run(cmd_dl, check=True)

    cmd_clean = [
        "ffmpeg", "-y", "-i", "reel.mp4",
        "-map_metadata", "-1",
        "-c:v", "libx264", "-crf", "23",
        "-c:a", "aac", "reel_clean.mp4"
    ]
    subprocess.run(cmd_clean, check=True)

    cmd_thumb = [
        "ffmpeg", "-y", "-ss", "00:00:01", "-i", "reel_clean.mp4",
        "-vframes", "1", "-q:v", "2", "thumb.jpg"
    ]
    subprocess.run(cmd_thumb, check=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bot active hai! Instagram Reel ka link bhejo.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "instagram.com" not in url:
        await update.message.reply_text("❌ Kripya valid Instagram link bhejein.")
        return

    await update.message.reply_text("⏳ Reel download aur clean ho rahi hai...")
    try:
        process_reel(url)
        await update.message.reply_document(document=open("reel_clean.mp4", "rb"), caption="✅ Processed Video")
        await update.message.reply_photo(photo=open("thumb.jpg", "rb"), caption="🖼 Auto Thumbnail")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_link))
    app.run_polling()

if __name__ == "__main__":
    main()
  
