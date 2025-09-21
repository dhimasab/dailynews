from telethon import TelegramClient, events
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import requests
import pytz
import os
import base64
from datetime import datetime

print("=== Bot Telethon starting up... ===", flush=True)

# API dari env
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
print(f"API_ID & API_HASH loaded dari ENV. API_ID={api_id}", flush=True)

# Nama session file
session_name = "session"
session_file = session_name + ".session"

# Ambil session dalam bentuk base64 dari ENV → decode → simpan jadi .session
session_b64 = os.getenv("SESSION")
if session_b64:
    with open(session_file, "wb") as f:
        f.write(base64.b64decode(session_b64))
    print(f"Session berhasil ditulis ke {session_file}", flush=True)

# Target (username & ID) dari env
TARGET_USERNAME = os.getenv("TARGET_USERNAME")
TARGET_ID = int(os.getenv("TARGET_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Init Telethon
client = TelegramClient(session_name, api_id, api_hash)

# State
last_question_id = None
collector_task = None   # task async untuk kumpulin balasan

async def collect_responses():
    """Tunggu 60 detik, lalu ambil bubble terpanjang setelah pertanyaan terakhir"""
    global last_question_id, collector_task
    print("[Collector] Mulai kumpulin balasan selama 60 detik...", flush=True)
    await asyncio.sleep(60)

    responses = await client.get_messages(TARGET_ID, min_id=last_question_id, limit=10)
    print(f"[Collector] Jumlah pesan ditemukan: {len(responses)}", flush=True)

    if not responses:
        print("[Collector] Tidak ada balasan dari Elfa.", flush=True)
    else:
        longest_msg = max(responses, key=lambda m: len(m.text or ""), default=None)
        if longest_msg and longest_msg.text:
            final_text = longest_msg.text
            print("✅ Balasan final dari Elfa:", final_text[:120], "...", flush=True)
            try:
                res = requests.post(WEBHOOK_URL, json={"sender": "Elfa", "message": final_text})
                print(f"[Webhook] Status: {res.status_code}", flush=True)
            except Exception as e:
                print("[Webhook] Error:", e, flush=True)

    collector_task = None  # reset setelah selesai

# Event listener → tiap bubble Elfa masuk
@client.on(events.NewMessage(from_users=TARGET_ID))
async def handler(event):
    global collector_task
    if last_question_id is None:
        return
    if collector_task is None:  # hanya bikin collector sekali
        print(f"[Handler] Balasan pertama dari Elfa (id={event.id}), mulai collector...", flush=True)
        collector_task = asyncio.create_task(collect_responses())
    else:
        print(f"[Handler] Bubble tambahan dari Elfa (id={event.id}), collector sudah jalan.", flush=True)

# Fungsi kirim pesan terjadwal
async def scheduled_message():
    global last_question_id
    target = await client.get_entity(TARGET_USERNAME)
    sent = await client.send_message(
        target,
        "Berikan update news, project web3 dan hot topik CT hari. Batasi hasilnya maksimal 3400 karakter"
    )
    last_question_id = sent.id
    print(f"[Scheduler] Pesan terjadwal dikirim (id={last_question_id}) @ {datetime.now()}", flush=True)

# Main loop
async def main():
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Jakarta"))
    scheduler.add_job(scheduled_message, "cron", hour=15, minute=47)
    scheduler.start()
    print("Scheduler sudah aktif, menunggu event/pesan masuk...", flush=True)
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
