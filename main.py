from telethon import TelegramClient, events
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import requests
import pytz
import os
import base64
from datetime import datetime

print("=== Bot Telethon starting up... ===", flush=True)

# Helper ambil ENV (wajib ada)
def get_env_str(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise ValueError(f"ENV {name} wajib diisi")
    return val

def get_env_int(name: str) -> int:
    val = os.getenv(name)
    if not val:
        raise ValueError(f"ENV {name} wajib diisi")
    return int(val)

# API dari ENV
api_id = get_env_int("API_ID")
api_hash = get_env_str("API_HASH")
print(f"API_ID & API_HASH loaded dari ENV. API_ID={api_id}", flush=True)

# Nama session file
session_name = "session"
session_file = session_name + ".session"

# Ambil session dari ENV → decode → simpan
session_b64 = get_env_str("SESSION")
with open(session_file, "wb") as f:
    f.write(base64.b64decode(session_b64))
print(f"Session berhasil ditulis ke {session_file}", flush=True)

# Target & webhook dari ENV
TARGET_USERNAME = get_env_str("TARGET_USERNAME")
TARGET_ID = get_env_int("TARGET_ID")
WEBHOOK_URL = get_env_str("WEBHOOK_URL")

# Scheduler config dari ENV
SCHEDULE_HOUR = get_env_int("SCHEDULE_HOUR")
SCHEDULE_MINUTE = get_env_int("SCHEDULE_MINUTE")
RESPONSE_DELAY = get_env_int("RESPONSE_DELAY")  # detik
QUESTION_TEXT = get_env_str("QUESTION_TEXT")

# Init Telethon
client = TelegramClient(session_name, api_id, api_hash)

# State
last_question_id = None
collector_task = None   # task async untuk kumpulin balasan

async def collect_responses():
    """Tunggu sesuai RESPONSE_DELAY, lalu ambil bubble terpanjang setelah pertanyaan terakhir"""
    global last_question_id, collector_task
    print(f"[Collector] Mulai kumpulin balasan selama {RESPONSE_DELAY} detik...", flush=True)
    await asyncio.sleep(RESPONSE_DELAY)

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
    sent = await client.send_message(target, QUESTION_TEXT)
    last_question_id = sent.id
    print(f"[Scheduler] Pesan terjadwal dikirim (id={last_question_id}) @ {datetime.now()}", flush=True)

# Main loop
async def main():
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Jakarta"))
    scheduler.add_job(scheduled_message, "cron", hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE)
    scheduler.start()
    print(f"Scheduler sudah aktif @ {SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d}, menunggu event/pesan masuk...", flush=True)
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
