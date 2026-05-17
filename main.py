import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

logging.basicConfig(level=logging.INFO)

# --- ENVIRONMENT VARIABLES ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
SOURCE_CHAT = os.getenv("SOURCE_CHAT")
TARGET_CHAT = os.getenv("TARGET_CHAT")  # Yaha par us BOT ka username aayega (E.g., @Complete_Bot_Username)

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
    "my_userbot", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    session_string=SESSION_STRING,
    ipv6=False
)

@app.on_message(filters.chat(SRC))
async def forward_messages(client: Client, message: Message):
    try:
        # Note: Kuch bots forward tag wale messages accept nahi karte (unhe lagta hai spam hai).
        # Isliye hum 'message.forward' ki jagah 'message.copy' use kar rahe hain.
        # Ye samne wale bot ko aisa lagega jaise aapne text khud type karke bheja hai.
        await message.copy(TG_CHAT)
        logging.info(f"Message successfully sent to bot! ID: {message.id}")
    except Exception as e:
        logging.error(f"Error during sending to bot: {e}")

if __name__ == "__main__":
    print("Userbot Bot-Forwarding ke liye Render par start ho raha hai...")
    app.run()
  
