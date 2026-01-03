import os
import uuid
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN غير موجود")

USER_URLS = {}

# إعدادات عامة لـ yt-dlp (مهمة)
BASE_YDL_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    },
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📥 أرسل رابط فيديو من:\n"
        "YouTube • Facebook • TikTok • Instagram\n"
        "ثم اختر الجودة أو الصوت فقط"
    )

async def receive_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith("http"):
        await update.message.reply_text("❌ الرابط غير صحيح")
        return

    USER_URLS[update.effective_user.id] = url

    keyboard = [
        [
            InlineKeyboardButton("🎥 360p", callback_data="360"),
            InlineKeyboardButton("🎥 720p", callback_data="720"),
        ],
        [
            InlineKeyboardButton("🎵 صوت فقط (MP3)", callback_data="mp3"),
        ],
    ]

    await update.message.reply_text(
        "اختر الصيغة:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    url = USER_URLS.get(user_id)

    if not url:
        await query.edit_message_text("❌ أعد إرسال الرابط")
        return

    choice = query.data
    file_id = str(uuid.uuid4())

    await query.edit_message_text("⏳ جاري التحميل...")

    try:
        # ===== صوت فقط =====
        if choice == "mp3":
            output = f"{file_id}.mp3"
            ydl_opts = BASE_YDL_OPTS | {
                "format": "bestaudio/best",
                "outtmpl": output,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            with open(output, "rb") as audio:
                await context.bot.send_audio(
                    chat_id=query.message.chat_id,
                    audio=audio,
                )

        # ===== فيديو =====
        else:
            output = f"{file_id}.mp4"
            ydl_opts = BASE_YDL_OPTS | {
                "format": f"bestvideo[height<={choice}]+bestaudio/best",
                "merge_output_format": "mp4",
                "outtmpl": output,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            with open(output, "rb") as video:
                await context.bot.send_video(
                    chat_id=query.message.chat_id,
                    video=video,
                    supports_streaming=True,
                )

    except Exception as e:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="❌ فشل التحميل\nقد يكون الفيديو خاصًا أو غير مدعوم"
        )

    finally:
        for f in os.listdir():
            if f.startswith(file_id):
                os.remove(f)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_url))
    app.add_handler(CallbackQueryHandler(handle_choice))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
