# --- PYTHON LOOP BUG FIX (LINE 1) ---
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
from pyrogram.raw.functions.channels import GetChannels

logging.basicConfig(level=logging.INFO)

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

# Sirf hamare specific source chat ke messages ko capture karega
@app.on_message(filters.chat(SRC))
async def forward_messages(client: Client, message: Message):
    try:
        # Message direct target par copy hoga
        await message.copy(TG_CHAT)
        logging.info(f"🎉 Message successfully copied! ID: {message.id}")
    except Exception as e:
        logging.error(f"⚠️ Forwarding failed for message ID {message.id}: {e}")

# --- FLASK SERVER ---
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Forwarder Bot is perfectly Live!"

@flask_app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

Thread(target=run_flask, daemon=True).start()

async def start_bot():
    try:
        await app.start()
        logging.info("🚀 Userbot connected to Telegram successfully!")
        
        # Core Peer Resolution Fix: Startup par hi chats ko database me force cache karna
        logging.info("🔄 Syncing Source and Target chats...")
        try:
            src_peer = await app.resolve_peer(SRC)
            logging.info(f"✅ Source Chat Synced successfully.")
        except Exception as e:
            logging.error(f"❌ Could not resolve Source Chat ({SRC}). Make sure username is correct and joined: {e}")
            
        try:
            target_peer = await app.resolve_peer(TG_CHAT)
            logging.info(f"✅ Target Chat Synced successfully.")
        except Exception as e:
            logging.error(f"❌ Could not resolve Target Chat ({TG_CHAT}). Make sure your account has started/joined it: {e}")

        logging.info("🟢 Everything is ready. Bot is listening for new messages...")
        
    except Exception as init_err:
        logging.error(f"❌ Critical Bot Initialization Error: {init_err}")
        
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    main_loop = asyncio.get_event_loop()
    main_loop.create_task(start_bot())
    main_loop.run_forever()
