import os
import logging
import asyncio
from flask import Flask, request
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

# --- FLASK SERVER & LIFECYCLE ---
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot is Live and Active!"

# Render jab ping karega toh ye route confirm karega ki bot chal raha hai
@flask_app.route('/webhook', map_options=dict(strict_slashes=False))
def webhook():
    return "OK", 200

async def start_bot():
    await app.start()
    logging.info("Pyrogram Userbot Started successfully!")
    # Keep alive loop inside async task
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    # Pyrogram ko background thread/loop me start karna aur flask ko main thread me run karna
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())
    
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)
