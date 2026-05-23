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
    return "✅ Premium Broadcast Bot Running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

Thread(target=run_web).start()

# ==========================================
# DATABASE
# ==========================================

db = sqlite3.connect(
    "users.db",
    check_same_thread=False
)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")

db.commit()

# ==========================================
# BOT CLIENT
# ==========================================

app = Client(
    "PremiumBroadcastBot",
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
# START COMMAND
# ==========================================

@app.on_message(filters.command("start"))
async def start(_, message):

    user_id = message.from_user.id

    await save_user(user_id)

    text = """
    Hey 👋 Welcome 🤗 I'm Airaa 😊

🤖 Developed By Prime
"""

    await message.reply_text(text)

# ==========================================
# HELP COMMAND
# ==========================================

@app.on_message(filters.command("help"))
async def help_cmd(_, message):

    text = """
📚 Broadcast Guide

1. Send any message
2. Reply to that message
3. Use:

/broadcast

✅ Supports:
• Premium Emojis
• Photos
• Videos
• Stickers
• GIFs
• Text
"""

    await message.reply_text(text)

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

    await message.reply_text(
        f"👥 Total Users: {total}"
    )

# ==========================================
# BROADCAST SYSTEM
# ==========================================

@app.on_message(filters.command("broadcast"))
async def broadcast(client, message):

    if message.from_user.id != OWNER_ID:

        return await message.reply_text(
            "Papa Ko bhej BKL 😂"
        )

    if not message.reply_to_message:

        return await message.reply_text(
            "⚠️ Reply to any message for broadcast"
        )

    users = cursor.execute(
        "SELECT user_id FROM users"
    ).fetchall()

    total = 0
    failed = 0

    status = await message.reply_text(
        "📢 Broadcasting Started..."
    )

    for user in users:

        user_id = user[0]

        try:

            await message.reply_to_message.copy(
                user_id
            )

            total += 1

        except Exception as e:

            print(e)

            failed += 1

    await status.edit_text(
        f"✅ Broadcast Completed\n\n"
        f"👥 Success: {total}\n"
        f"❌ Failed: {failed}"
    )

# ==========================================
# AUTO SAVE USERS
# ==========================================

@app.on_message(filters.private)
async def auto_save(_, message):

    user_id = message.from_user.id

    await save_user(user_id)

# ==========================================
# BOT ONLINE LOG
# ==========================================

print("✅ Premium Broadcast Bot Started")

# ==========================================
# RUN BOT
# ==========================================

app.run()
