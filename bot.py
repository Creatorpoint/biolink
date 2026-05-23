import os
import re
from threading import Thread
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
from dotenv import load_dotenv

# =========================
# FLASK WEB SERVER
# =========================

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "✅ Bio Guard Bot Running Successfully"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

Thread(target=run_web).start()

# =========================
# LOAD ENV
# =========================

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

# =========================
# BOT CLIENT
# =========================

app = Client(
    "BioGuardBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# =========================
# LINK DETECTOR
# =========================

LINK_REGEX = r"(https?://|t\.me/|telegram\.me/|www\.|\.com|\.net|\.in|@)"

# =========================
# MEMORY
# =========================

old_usernames = {}

# =========================
# ADMIN CHECK
# =========================

async def is_admin(client, chat_id, user_id):
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in ["administrator", "owner"]

# =========================
# START COMMAND
# =========================

@app.on_message(filters.command("start"))
async def start(_, message):

    text = """
✅ Advanced Bio Guard Bot Active

👮 Features:
• Bio Link Remover
• Username Change Detector
• Auto Mute
• Auto Delete
• Admin Commands
• User ID Finder

🤖 Developed By: @PREMGUPTA2M
"""

    await message.reply_text(text)

# =========================
# HELP COMMAND
# =========================

@app.on_message(filters.command("help"))
async def help_cmd(_, message):

    text = """
📚 Commands List

/start - Start bot
/help - Help menu
/id - Get user id

Admin Commands:
/mute
/unmute
/ban
/unban
"""

    await message.reply_text(text)

# =========================
# USER ID COMMAND
# =========================

@app.on_message(filters.command("id"))
async def get_id(_, message):

    user = message.from_user

    await message.reply_text(
        f"👤 Name: {user.first_name}\n"
        f"🆔 User ID: `{user.id}`"
    )

# =========================
# MUTE COMMAND
# =========================

@app.on_message(filters.command("mute") & filters.group)
async def mute_user(client, message):

    admin = await is_admin(
        client,
        message.chat.id,
        message.from_user.id
    )

    if not admin:
        return await message.reply_text(
            "❌ You are not admin"
        )

    if not message.reply_to_message:
        return await message.reply_text(
            "⚠️ Reply to a user"
        )

    target = message.reply_to_message.from_user

    await client.restrict_chat_member(
        message.chat.id,
        target.id,
        ChatPermissions()
    )

    await message.reply_text(
        f"🔇 {target.mention} muted"
    )

# =========================
# UNMUTE COMMAND
# =========================

@app.on_message(filters.command("unmute") & filters.group)
async def unmute_user(client, message):

    admin = await is_admin(
        client,
        message.chat.id,
        message.from_user.id
    )

    if not admin:
        return

    if not message.reply_to_message:
        return await message.reply_text(
            "⚠️ Reply to user"
        )

    target = message.reply_to_message.from_user

    await client.unban_chat_member(
        message.chat.id,
        target.id
    )

    await message.reply_text(
        f"🔊 {target.mention} unmuted"
    )

# =========================
# BAN COMMAND
# =========================

@app.on_message(filters.command("ban") & filters.group)
async def ban_user(client, message):

    admin = await is_admin(
        client,
        message.chat.id,
        message.from_user.id
    )

    if not admin:
        return

    if not message.reply_to_message:
        return await message.reply_text(
            "⚠️ Reply to user"
        )

    target = message.reply_to_message.from_user

    await client.ban_chat_member(
        message.chat.id,
        target.id
    )

    await message.reply_text(
        f"🚫 {target.mention} banned"
    )

# =========================
# UNBAN COMMAND
# =========================

@app.on_message(filters.command("unban") & filters.group)
async def unban_user(client, message):

    admin = await is_admin(
        client,
        message.chat.id,
        message.from_user.id
    )

    if not admin:
        return

    if not message.reply_to_message:
        return await message.reply_text(
            "⚠️ Reply to user"
        )

    target = message.reply_to_message.from_user

    await client.unban_chat_member(
        message.chat.id,
        target.id
    )

    await message.reply_text(
        f"✅ {target.mention} unbanned"
    )

# =========================
# BIO LINK CHECKER
# =========================

@app.on_message(filters.group & filters.text)
async def bio_checker(client, message):

    user = message.from_user

    if not user:
        return

    try:

        full_user = await client.get_users(user.id)

        bio = full_user.bio or ""

        if re.search(LINK_REGEX, bio, re.IGNORECASE):

            try:
                await message.delete()
            except:
                pass

            try:
                await client.restrict_chat_member(
                    message.chat.id,
                    user.id,
                    ChatPermissions()
                )
            except:
                pass

            await message.chat.send_message(
                f"🚫 {user.mention}\n\n"
                f"bkl pehle link remove kr bio se 😹"
            )

    except Exception as e:
        print(e)

# =========================
# USERNAME CHANGE DETECTOR
# =========================

@app.on_message(filters.group)
async def username_tracker(_, message):

    user = message.from_user

    if not user:
        return

    current_username = user.username

    if user.id not in old_usernames:
        old_usernames[user.id] = current_username
        return

    old_username = old_usernames[user.id]

    if old_username != current_username:

        await message.chat.send_message(
            f"⚠️ {user.mention} changed username\n\n"
            f"Old Username: @{old_username}\n"
            f"New Username: @{current_username}"
        )

        old_usernames[user.id] = current_username

# =========================
# START BOT
# =========================

print("✅ Bio Guard Bot Started Successfully")

app.run()
