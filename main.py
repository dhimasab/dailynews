from telethon import TelegramClient, events
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import requests
import pytz
import os
import base64
from datetime import datetime

# API dari env
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# Nama session file
session_name = "session"
session_file = session_name + ".session"

# Ambil session dalam bentuk base64 dari ENV → decode → simpan jadi .session
session_b64 = os.getenv("SESSION")
if session_b64:
    with open(session_file, "wb") as f:
        f.write(base64.b64decode(session_b64))

# Target (username & ID) dari env
TARGET_USERNAME = os.getenv("TARGET_USERNAME")
TARGET_ID = int(os.getenv("TARGET_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Init Telethon
client = TelegramClient(session_name, api_id, api_hash)

# Event listener
@client.on(events.NewMessage(from_users=TARGET_ID))
async def handler(event):
    print("Pesan diterima dari Elfa, tunggu 60 detik sebelum respon final...")
    await asyncio.sleep(60)

    # Ambil ulang pesan terbaru biar bukan "Thinking..."
    messages = await client.get_messages(TARGET_ID, limit=1)
    if messages:
        final_text = messages[0].text
        print("Balasan final dari Elfa:", final_text)

        # Kirim ke webhook n8n
        payload = {"sender": "Elfa", "message": final_text}
        try:
            res = requests.post(WEBHOOK_URL, json=payload)
            print("Webhook status:", res.status_code)
        except Exception as e:
            print("Gagal kirim webhook:", e)

# Fungsi kirim pesan terjadwal
async def scheduled_message():
    target = await client.get_entity(TARGET_USERNAME)
    await client.send_message(target, "Berikan update news, project web3 dan hot topik CT hari. Batasi hasilnya maksimal 3400 karakter")
    print("Pesan terjadwal dikirim:", datetime.now())

# Main loop
async def main():
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Jakarta"))
    scheduler.add_job(scheduled_message, "cron", hour=2, minute=21)  # 14:30 WIB
    scheduler.start()

    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
