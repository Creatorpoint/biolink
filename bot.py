import os
import re
from threading import Thread
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
from dotenv import load_dotenv

# ==========================================
# WEB SERVER FOR RENDER
# ==========================================

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "✅ Bio Guard Bot Running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

Thread(target=run_web).start()

# ==========================================
# LOAD ENV
# ==========================================

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

# ==========================================
# BOT CLIENT
# ==========================================

app = Client(
    "BioGuardBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ==========================================
# LINK REGEX
# ==========================================

LINK_REGEX = r"(https?://\S+|t\.me/\S+|telegram\.me/\S+|www\.\S+|@\w+|\.com|\.net|\.in)"

# ==========================================
# USERNAME MEMORY
# ==========================================

old_usernames = {}

# ==========================================
# ADMIN CHECK
# ==========================================

async def is_admin(client, chat_id, user_id):

    member = await client.get_chat_member(
        chat_id,
        user_id
    )

    return member.status in [
        "administrator",
        "owner"
    ]

# ==========================================
# START COMMAND
# ==========================================

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

🤖 Developed By: PREM
"""

    await message.reply_text(text)

# ==========================================
# HELP COMMAND
# ==========================================

@app.on_message(filters.command("help"))
async def help_cmd(_, message):

    text = """
📚 Commands List

/start - Start Bot
/help - Help Menu
/id - Get User ID

Admin Commands:
/mute
/unmute
/ban
/unban
"""

    await message.reply_text(text)

# ==========================================
# USER ID COMMAND
# ==========================================

@app.on_message(filters.command("id"))
async def get_id(_, message):

    user = message.from_user

    await message.reply_text(
        f"👤 Name: {user.first_name}\n"
        f"🆔 User ID: `{user.id}`"
    )

# ==========================================
# MUTE COMMAND
# ==========================================

@app.on_message(filters.command("mute") & filters.group)
async def mute_user(client, message):

    if not await is_admin(
        client,
        message.chat.id,
        message.from_user.id
    ):
        return await message.reply_text(
            "❌ You are not admin"
        )

    if not message.reply_to_message:
        return await message.reply_text(
            "⚠️ Reply to a user"
        )

    target = message.reply_to_message.from_user

    try:

        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            permissions=ChatPermissions()
        )

        await message.reply_text(
            f"🔇 {target.mention} muted"
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Error:\n{e}"
        )

# ==========================================
# UNMUTE COMMAND
# ==========================================

@app.on_message(filters.command("unmute") & filters.group)
async def unmute_user(client, message):

    if not await is_admin(
        client,
        message.chat.id,
        message.from_user.id
    ):
        return

    if not message.reply_to_message:
        return await message.reply_text(
            "⚠️ Reply to user"
        )

    target = message.reply_to_message.from_user

    try:

        await client.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )

        await message.reply_text(
            f"🔊 {target.mention} unmuted"
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Error:\n{e}"
        )

# ==========================================
# BAN COMMAND
# ==========================================

@app.on_message(filters.command("ban") & filters.group)
async def ban_user(client, message):

    if not await is_admin(
        client,
        message.chat.id,
        message.from_user.id
    ):
        return

    if not message.reply_to_message:
        return await message.reply_text(
            "⚠️ Reply to user"
        )

    target = message.reply_to_message.from_user

    try:

        await client.ban_chat_member(
            message.chat.id,
            target.id
        )

        await message.reply_text(
            f"🚫 {target.mention} banned"
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Error:\n{e}"
        )

# ==========================================
# UNBAN COMMAND
# ==========================================

@app.on_message(filters.command("unban") & filters.group)
async def unban_user(client, message):

    if not await is_admin(
        client,
        message.chat.id,
        message.from_user.id
    ):
        return

    if not message.reply_to_message:
        return await message.reply_text(
            "⚠️ Reply to user"
        )

    target = message.reply_to_message.from_user

    try:

        await client.unban_chat_member(
            message.chat.id,
            target.id
        )

        await message.reply_text(
            f"✅ {target.mention} unbanned"
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Error:\n{e}"
        )

# ==========================================
# BIO LINK CHECKER
# ==========================================

@app.on_message(filters.group)
async def bio_checker(client, message):

    user = message.from_user

    if not user:
        return

    if user.is_bot:
        return

    try:

        member = await client.get_chat_member(
            message.chat.id,
            user.id
        )

        # Ignore admins
        if member.status in [
            "administrator",
            "owner"
        ]:
            return

        full_user = await client.get_users(
            user.id
        )

        bio = full_user.bio or ""

        print(f"{user.first_name} BIO => {bio}")

        if re.search(
            LINK_REGEX,
            bio,
            re.IGNORECASE
        ):

            # Delete message
            try:
                await message.delete()
            except Exception as e:
                print("DELETE ERROR:", e)

            # Mute user
            try:
                await client.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=user.id,
                    permissions=ChatPermissions()
                )
            except Exception as e:
                print("MUTE ERROR:", e)

            # Send warning
            await client.send_message(
                message.chat.id,
                f"🚫 {user.mention}\n\n"
                f"bkl pehle link remove kr bio se 😹"
            )

    except Exception as e:
        print("BIO ERROR:", e)

# ==========================================
# USERNAME CHANGE DETECTOR
# ==========================================

@app.on_message(filters.group)
async def username_tracker(client, message):

    user = message.from_user

    if not user:
        return

    current_username = user.username

    if user.id not in old_usernames:

        old_usernames[user.id] = current_username
        return

    old_username = old_usernames[user.id]

    if old_username != current_username:

        await client.send_message(
            message.chat.id,
            f"⚠️ {user.mention} changed username\n\n"
            f"Old Username: @{old_username}\n"
            f"New Username: @{current_username}"
        )

        old_usernames[user.id] = current_username

# ==========================================
# ONLINE LOG
# ==========================================

print("✅ Bio Guard Bot Started Successfully")

# ==========================================
# RUN BOT
# ==========================================

app.run()
