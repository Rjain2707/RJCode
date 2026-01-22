import requests
import os

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not BOT_TOKEN:
    print("❌ TELEGRAM_TOKEN is missing!")
if not CHANNEL_ID:
    print("❌ CHANNEL_ID is missing!")

if not BOT_TOKEN or not CHANNEL_ID:
    raise Exception("BOT_TOKEN or CHANNEL_ID is missing")

message = "🚀 Test message from GitHub Actions"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

payload = {
    "chat_id": CHANNEL_ID,
    "text": message
}

response = requests.post(url, data=payload)

if response.status_code == 200:
    print("✅ Telegram message sent successfully")
else:
    print("❌ Failed to send Telegram message:", response.status_code, response.text)

