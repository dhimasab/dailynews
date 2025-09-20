from telethon import TelegramClient, events
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import requests
import pytz
from datetime import datetime

# pakai api_id & api_hash kamu
api_id = 21369351
api_hash = "290e7d6666c8cd0df296217dc9f33cab"

# pakai session yang udah ada
client = TelegramClient("n8n_session", api_id, api_hash)

# username & id target
TARGET_USERNAME = "elfaai_bot"
TARGET_ID = 7394639228

# webhook n8n
WEBHOOK_URL = "https://n8n-21taaijwdbbi.tomat.sumopod.my.id/webhook/elfa"

# event listener
@client.on(events.NewMessage(from_users=TARGET_ID))
async def handler(event):
    print("Pesan diterima dari Elfa, tunggu 60 detik sebelum respon final...")
    await asyncio.sleep(60)

    # ambil ulang pesan terbaru biar bukan "Thinking..."
    messages = await client.get_messages(TARGET_ID, limit=1)
    if messages:
        final_text = messages[0].text
        print("Balasan final dari Elfa:", final_text)

        # kirim ke webhook n8n
        payload = {"sender": "Elfa", "message": final_text}
        try:
            res = requests.post(WEBHOOK_URL, json=payload)
            print("Webhook status:", res.status_code)
        except Exception as e:
            print("Gagal kirim webhook:", e)

# fungsi untuk kirim pesan terjadwal
async def scheduled_message():
    target = await client.get_entity(TARGET_USERNAME)
    await client.send_message(target, "Berikan update news, project web3 dan hot topik CT hari")
    print("Pesan terjadwal dikirim:", datetime.now())

async def main():
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Jakarta"))

    # jadwalkan tiap hari jam 14:30 WIB
    scheduler.add_job(scheduled_message, "cron", hour=14, minute=27)

    scheduler.start()

    # jalanin client terus
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
