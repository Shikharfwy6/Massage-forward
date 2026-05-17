# CRITICAL: Yeh 6 lines code me bilkul sabse upar (Line 1) honi chahiye.
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
from pyrogram import Client, filters
from pyrogram.types import Message

logging.basicConfig(level=logging.INFO)

# --- CONFIGURATION ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
SOURCE_CHATS_RAW = os.getenv("SOURCE_CHAT") # Ab isme multiple channels honge comma se separate
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

# Multiple channels ko handle karne ke liye logic
SRC_LIST = []
if SOURCE_CHATS_RAW:
    # Comma se split karke har channel ko clean aur parse karega
    for chat in SOURCE_CHATS_RAW.split(","):
        parsed = parse_chat(chat)
        if parsed:
            SRC_LIST.append(parsed)

TG_CHAT = parse_chat(TARGET_CHAT)

print(f"Monitoring channels: {SRC_LIST}")

# --- PYROGRAM CLIENT ---
app = Client(
    "forwarder_userbot", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    session_string=SESSION_STRING,
    ipv6=False
)

# filters.chat(SRC_LIST) ab puri list ko ek sath monitor karega
@app.on_message(filters.chat(SRC_LIST))
async def forward_messages(client: Client, message: Message):
    try:
        await message.copy(TG_CHAT)
        logging.info(f"Message copied from {message.chat.title or message.chat.id}! ID: {message.id}")
    except Exception as e:
        logging.error(f"Forward error: {e}")

# --- FLASK SERVER ---
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Multi-Channel Forwarder Bot is Live!"

@flask_app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

Thread(target=run_flask, daemon=True).start()

async def start_bot():
    await app.start()
    logging.info("Pyrogram Multi-Channel Userbot Started successfully!")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    main_loop = asyncio.get_event_loop()
    main_loop.create_task(start_bot())
    main_loop.run_forever()
