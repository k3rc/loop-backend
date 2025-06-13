import os, requests, shutil
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler, CommandHandler

API = os.getenv("BACKEND_URL", "https://loop-backend-production.up.railway.app")
BOT_TOKEN = os.getenv("BOT_TOKEN")  # задаёшь в Railway Variables
TITLE, ARTIST, GENRE, ALBUM, AUDIO, COVER = range(6)

def start(update, ctx):
    update.message.reply_text("Send /upload to upload a new track")

def upload_cmd(update, ctx):
    update.message.reply_text("Title?")
    return TITLE

def get_title(update, ctx):
    ctx.user_data["title"] = update.message.text
    update.message.reply_text("Artist?")
    return ARTIST

def get_artist(update, ctx):
    ctx.user_data["artist"] = update.message.text
    update.message.reply_text("Genre?")
    return GENRE

def get_genre(update, ctx):
    ctx.user_data["genre"] = update.message.text
    update.message.reply_text("Album?")
    return ALBUM

def get_album(update, ctx):
    ctx.user_data["album"] = update.message.text
    update.message.reply_text("Send audio file (.mp3)")
    return AUDIO

def get_audio(update, ctx):
    file = update.message.audio or update.message.document
    if not file:
        update.message.reply_text("Not audio, try again")
        return AUDIO
    audio_path = file.get_file().download()
    ctx.user_data["audio_path"] = audio_path
    update.message.reply_text("Send cover image (jpg/png)")
    return COVER

def get_cover(update, ctx):
    img = update.message.photo[-1] if update.message.photo else update.message.document
    cover_path = img.get_file().download()
    ctx.user_data["cover_path"] = cover_path
    # Upload to backend
    data = {
        'title':  ctx.user_data["title"],
        'artist': ctx.user_data["artist"],
        'genre':  ctx.user_data["genre"],
        'album':  ctx.user_data["album"],
    }
    files = {
        'file':  open(ctx.user_data["audio_path"], 'rb'),
        'cover': open(cover_path, 'rb')
    }
    r = requests.post(f"{API}/upload", data=data, files=files)
    update.message.reply_text("Uploaded!" if r.ok else f"Error: {r.text}")
    return ConversationHandler.END

def cancel(update, ctx):
    update.message.reply_text("Cancelled")
    return ConversationHandler.END

up = Updater(BOT_TOKEN)
conv = ConversationHandler(
    entry_points=[CommandHandler('upload', upload_cmd)],
    states={
        TITLE:  [MessageHandler(Filters.text & ~Filters.command, get_title)],
        ARTIST: [MessageHandler(Filters.text & ~Filters.command, get_artist)],
        GENRE:  [MessageHandler(Filters.text & ~Filters.command, get_genre)],
        ALBUM:  [MessageHandler(Filters.text & ~Filters.command, get_album)],
        AUDIO:  [MessageHandler(Filters.audio | Filters.document, get_audio)],
        COVER:  [MessageHandler(Filters.photo | Filters.document, get_cover)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
up.dispatcher.add_handler(CommandHandler('start', start))
up.dispatcher.add_handler(conv)
up.start_polling(); up.idle()
