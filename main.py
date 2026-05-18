# --- PYTHON LOOP BUG FIX ---
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

app = Client(
    "forwarder_userbot", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    session_string=SESSION_STRING,
    ipv6=False
)

# Global error handler lagaya hai taaki invalid peer par bot stop na ho
@app.on_message(filters.chat(SRC))
async def forward_messages(client: Client, message: Message):
    try:
        # Message ko send karne ki koshish
        await message.copy(TG_CHAT)
        logging.info(f"Message copied successfully! ID: {message.id}")
    except Exception as e:
        # Agar peer invalid ya koi aur issue aayega toh yahan log hoga, bot chalta rahega
        logging.error(f"Skipping message due to error: {e}")

# --- FLASK SERVER ---
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Forwarder Bot is Active!"

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
        logging.info("Pyrogram Userbot Connected Successfully!")
        
        # Ek baar target chat ko sync kar lete hain taaki ID register ho jaye
        try:
            await app.get_chat(TG_CHAT)
            logging.info("Target chat successfully verified and synced!")
        except Exception as e:
            logging.warning(f"Target chat sync warning: {e}. Make sure your account joined/started the target!")
            
    except Exception as init_err:
        logging.error(f"Bot start error: {init_err}")
        
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    main_loop = asyncio.get_event_loop()
    main_loop.create_task(start_bot())
    main_loop.run_forever()
