# CRITICAL: Yeh 6 lines code me bilkul sabse upar (Line 1) honi chahiye.
# Pyrogram import hone se pehle loop initialize hona zaroori hai.
import asyncio
try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

import os
import logging
from threading import Thread
from flask import Flask

# Pyrogram ko Flask aur loop setup ke BAAD import kar rahe hain
from pyrogram import Client, filters
from pyrogram.types import Message

logging.basicConfig(level=logging.INFO)

# --- CONFIGURATION ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
SOURCE_CHAT = os.getenv("SOURCE_CHAT")
TARGET_CHAT = os.getenv("TARGET_CHAT")

def parse_chat(chat_str):
    if not chat_str:
        return None
    chat_str = chat_str.strip()
    if chat_str.startswith("@"):
        return chat_str
    try:
        return int(chat_str)
    except ValueError:
        return chat_str

SRC = parse_chat(SOURCE_CHAT)
TG_CHAT = parse_chat(TARGET_CHAT)

# --- PYROGRAM CLIENT ---
app = Client(
    "forwarder_userbot", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    session_string=SESSION_STRING,
    ipv6=False
)

@app.on_message(filters.chat(SRC))
async def forward_messages(client: Client, message: Message):
    try:
        await message.copy(TG_CHAT)
        logging.info(f"Message copied! ID: {message.id}")
    except Exception as e:
        logging.error(f"Forward error: {e}")

# --- FLASK SERVER ---
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot is Live and Active!"

@flask_app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

# Flask ko alag thread me chalayenge taaki port binding fast ho
Thread(target=run_flask, daemon=True).start()
print("Flask server started to bypass Render port scan.")

async def start_bot():
    await app.start()
    logging.info("Pyrogram Userbot Started successfully!")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    # Jo loop humne upar create kiya tha, usi me bot task run karenge
    main_loop = asyncio.get_event_loop()
    main_loop.create_task(start_bot())
    main_loop.run_forever()
