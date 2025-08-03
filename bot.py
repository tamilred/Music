from pyrogram import Client, filters
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()
bot = Client("audio_bot",
             api_id=int(os.getenv("23794727")),
             api_hash=os.getenv("35140d8eefc686d2c60da1fb622dcdde"),
             bot_token=os.getenv("7862056115:AAFNI7xK67X6VdUeqhC-5Jjtp_CI1Djagm4"))

mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["audio_bot"]
users = db["users"]
audios = db["audios"]
tokens = db["tokens"]

ADMIN_ID = int(os.getenv("7299955528"))
CHANNEL = os.getenv("CHANNEL_USERNAME")
ACCESS_PASSWORD = os.getenv("ACCESS_PASSWORD")
SUB_DAYS = int(os.getenv("SUBSCRIPTION_DAYS"))

@bot.on_message(filters.command("start"))
async def start_cmd(client, message):
    uid = message.from_user.id
    args = message.text.split()
    user = users.find_one({"user_id": uid})

    if uid == ADMIN_ID:
        return await message.reply("👑 Welcome, Admin!")

    if user and user.get("expires_at") > datetime.utcnow():
        return await message.reply("✅ You're already verified.")

    if len(args) == 2 and args[1].startswith("access_"):
        token = args[1].replace("access_", "")
        entry = tokens.find_one({"token": token, "used": False})
        if entry:
            users.insert_one({
                "user_id": uid,
                "expires_at": datetime.utcnow() + timedelta(days=SUB_DAYS)
            })
            tokens.update_one({"token": token}, {"$set": {"used": True}})
            return await message.reply("✅ Access granted.")
        else:
            return await message.reply("❌ Invalid or used link.")

    await message.reply("🔐 Enter the password to continue:")

@bot.on_message(filters.text & filters.private)
async def password_check(client, message):
    uid = message.from_user.id
    if uid == ADMIN_ID or users.find_one({"user_id": uid}):
        return
    if message.text.strip() == ACCESS_PASSWORD:
        users.insert_one({
            "user_id": uid,
            "expires_at": datetime.utcnow() + timedelta(days=SUB_DAYS)
        })
        await message.reply("✅ Password correct. Access granted!")
    else:
        await message.reply("❌ Incorrect password.")

@bot.on_message(filters.command("playlist"))
async def show_playlist(client, message):
    uid = message.from_user.id
    if uid != ADMIN_ID:
        user = users.find_one({"user_id": uid})
        if not user or user["expires_at"] < datetime.utcnow():
            return await message.reply("❌ Subscription expired or not verified.")

    all_audios = list(audios.find().sort("uploaded_at", -1))
    if not all_audios:
        return await message.reply("📭 No audios uploaded yet.")

    txt = "🎵 Audio Playlist:

"
    for i, track in enumerate(all_audios, 1):
        txt += f"{i}. {track['title']}
"
    txt += "
Send /play <number> to listen."
    await message.reply(txt)

@bot.on_message(filters.command("play"))
async def play_audio(client, message):
    uid = message.from_user.id
    if uid != ADMIN_ID:
        user = users.find_one({"user_id": uid})
        if not user or user["expires_at"] < datetime.utcnow():
            return await message.reply("❌ Access denied.")

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await message.reply("❗ Usage: /play <number>")

    index = int(parts[1]) - 1
    all_audios = list(audios.find().sort("uploaded_at", -1))
    if index >= len(all_audios):
        return await message.reply("❌ Invalid number.")

    audio = all_audios[index]
    await message.reply_audio(audio["file_id"], caption=f"🎧 {audio['title']}", protect_content=True)

@bot.on_message(filters.command("upload") & filters.user(ADMIN_ID))
async def upload_cmd(client, message):
    await message.reply("🎵 Send me the audio file with caption as title.")

@bot.on_message(filters.audio & filters.user(ADMIN_ID))
async def handle_upload(client, message):
    if not message.caption:
        return await message.reply("❗ Please provide title in caption.")

    audios.insert_one({
        "file_id": message.audio.file_id,
        "title": message.caption,
        "uploaded_at": datetime.utcnow(),
        "uploaded_by": ADMIN_ID
    })
    await client.send_audio(CHANNEL, message.audio.file_id, caption=f"🎧 {message.caption}", protect_content=True)
    await message.reply("✅ Audio uploaded and sent to channel.")

bot.run()
