import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل رابط الفيديو")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("جاري التحميل...")

    ydl_opts = {"format": "mp4", "outtmpl": "video.%(ext)s"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    await update.message.reply_video(video=open("video.mp4", "rb"))

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, download))
app.run_polling()
