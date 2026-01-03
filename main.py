import os
import uuid
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp
import asyncio

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل رابط الفيديو")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("تحميل...")

    filename = f"{uuid.uuid4()}.mp4"  # اسم فريد لكل فيديو
    ydl_opts = {"format": "mp4", "outtmpl": filename}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await update.message.reply_video(video=open(filename, "rb"))
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)  # حذف الملف بعد الإرسال

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, download))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
