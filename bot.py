import os
import re
import glob
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8975456161:AAHSNLITEZ-JT45AEi_EI1KQzOKNWXw_4E0"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bot active hai! Instagram Reel ka link bhejo.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not ("instagram.com" in url or "instagr.am" in url):
        await update.message.reply_text("⚠️ Kripya valid Instagram Reel ka link bhejein.")
        return

    msg = await update.message.reply_text("⏳ Reel download ho rahi hai...")

    for f in glob.glob("temp_*.*"):
        try:
            os.remove(f)
        except Exception:
            pass

    chat_id = update.effective_chat.id
    raw_output = f"temp_raw_{chat_id}.%(ext)s"
    clean_output = f"temp_clean_{chat_id}.mp4"

    download_cmd = [
        "yt-dlp",
        "-f", "b[ext=mp4]/b",
        "-o", raw_output,
        url
    ]
    res = subprocess.run(download_cmd, capture_output=True, text=True)

    downloaded = glob.glob(f"temp_raw_{chat_id}.*")
    if not downloaded:
        await msg.edit_text("❌ Download fail ho gaya. Kripya check karein ki reel public hai.")
        return

    input_file = downloaded[0]
    await msg.edit_text("⚙️ Video clean aur process ho rahi hai...")

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-map_metadata", "-1",
        "-c:v", "copy",
        "-c:a", "copy",
        clean_output
    ]
    subprocess.run(ffmpeg_cmd, capture_output=True)

    send_file = clean_output if os.path.exists(clean_output) else input_file

    await msg.edit_text("📤 Telegram par upload ho rahi hai...")
    try:
        with open(send_file, "rb") as video:
            await update.message.reply_video(video=video, caption="✅ Video ready!")
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ Upload error: {str(e)}")

    for f in glob.glob(f"temp_*_{chat_id}.*"):
        try:
            os.remove(f)
        except Exception:
            pass

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot live aur ready hai...")
    app.run_polling()
    
