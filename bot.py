import os
import sqlite3
from threading import Thread
from flask import Flask
from pyrogram import Client, filters
from dotenv import load_dotenv

# ==========================================
# LOAD ENV
# ==========================================

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

# ==========================================
# FLASK WEB SERVER
# ==========================================

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "✅ Advanced Broadcast Bot Running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

Thread(target=run_web).start()

# ==========================================
# DATABASE
# ==========================================

db = sqlite3.connect(
    "broadcast.db",
    check_same_thread=False
)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS groups (
    group_id INTEGER PRIMARY KEY
)
""")

db.commit()

# ==========================================
# BOT CLIENT
# ==========================================

app = Client(
    "AdvancedBroadcastBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ==========================================
# SAVE USER
# ==========================================

async def save_user(user_id):

    cursor.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user_id,)
    )

    data = cursor.fetchone()

    if data is None:

        cursor.execute(
            "INSERT INTO users VALUES (?)",
            (user_id,)
        )

        db.commit()

# ==========================================
# SAVE GROUP
# ==========================================

async def save_group(group_id):

    cursor.execute(
        "SELECT * FROM groups WHERE group_id=?",
        (group_id,)
    )

    data = cursor.fetchone()

    if data is None:

        cursor.execute(
            "INSERT INTO groups VALUES (?)",
            (group_id,)
        )

        db.commit()

# ==========================================
# START COMMAND
# ==========================================

@app.on_message(filters.command("start"))
async def start(_, message):

    await save_user(message.from_user.id)

    text = """
✨hey welcome 🤗 I'm AIRAA 🎀
🤖 Developed By Prime
"""

    await message.reply_text(text)

# ==========================================
# SAVE GROUPS
# ==========================================

@app.on_message(filters.group)
async def group_save(_, message):

    await save_group(message.chat.id)

# ==========================================
# SAVE USERS
# ==========================================

@app.on_message(filters.private)
async def private_save(_, message):

    await save_user(message.from_user.id)

# ==========================================
# USER COUNT
# ==========================================

@app.on_message(filters.command("users"))
async def users_count(_, message):

    if message.from_user.id != OWNER_ID:
        return

    total = cursor.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    groups = cursor.execute(
        "SELECT COUNT(*) FROM groups"
    ).fetchone()[0]

    await message.reply_text(
        f"👥 Users: {total}\n"
        f"👨‍👩‍👦 Groups: {groups}"
    )

# ==========================================
# BROADCAST SYSTEM
# ==========================================

@app.on_message(filters.command("broadcast"))
async def broadcast(client, message):

    if message.from_user.id != OWNER_ID:

        return await message.reply_text(
            "YE KAAM PRIME PAPA SE HOGA BCHA 😂"
        )

    if not message.reply_to_message:

        return await message.reply_text(
            "⚠️ Reply to message for broadcast"
        )

    users = cursor.execute(
        "SELECT user_id FROM users"
    ).fetchall()

    groups = cursor.execute(
        "SELECT group_id FROM groups"
    ).fetchall()

    success = 0
    failed = 0

    status = await message.reply_text(
        "📢 Broadcasting Started..."
    )

    # USERS
    for user in users:

        try:

            await message.reply_to_message.copy(
                user[0]
            )

            success += 1

        except Exception as e:

            print(e)

            failed += 1

    # GROUPS
    for group in groups:

        try:

            await message.reply_to_message.copy(
                group[0]
            )

            success += 1

        except Exception as e:

            print(e)

            failed += 1

    await status.edit_text(
        f"✅ Broadcast Completed\n\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}"
    )

# ==========================================
# FORWARD USER REPLIES TO OWNER
# ==========================================

@app.on_message(filters.private & ~filters.command([
    "start",
    "broadcast",
    "users"
]))
async def forward_to_owner(client, message):

    if message.from_user.id == OWNER_ID:
        return

    user = message.from_user

    caption = (
        f"📩 New User Reply\n\n"
        f"👤 Name: {user.first_name}\n"
        f"🆔 ID: {user.id}\n"
        f"📛 Username: @{user.username}"
    )

    try:

        forwarded = await message.forward(
            OWNER_ID
        )

        await forwarded.reply_text(caption)

    except Exception as e:

        print(e)

# ==========================================
# OWNER REPLY SYSTEM
# ==========================================

@app.on_message(filters.private & filters.reply)
async def owner_reply(client, message):

    if message.from_user.id != OWNER_ID:
        return

    try:

        replied = message.reply_to_message

        if not replied.forward_from:
            return

        target_id = replied.forward_from.id

        if message.text:

            await client.send_message(
                target_id,
                f"📩 Owner Reply:\n\n{message.text}"
            )

        elif message.photo:
            await message.copy(target_id)

        elif message.video:
            await message.copy(target_id)

        elif message.sticker:
            await message.copy(target_id)

        elif message.document:
            await message.copy(target_id)

    except Exception as e:

        print(e)

# ==========================================
# ONLINE LOG
# ==========================================

print("✅ Advanced Broadcast Bot Started")

# ==========================================
# RUN BOT
# ==========================================

app.run()
