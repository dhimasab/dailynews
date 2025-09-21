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
else:
    print("WARNING: SESSION env tidak ditemukan!", flush=True)

# Target (username & ID) dari env
TARGET_USERNAME = os.getenv("TARGET_USERNAME")
TARGET_ID = int(os.getenv("TARGET_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

print(f"Target config loaded → USERNAME={TARGET_USERNAME}, ID={TARGET_ID}", flush=True)

# Init Telethon
client = TelegramClient(session_name, api_id, api_hash)

# Simpan ID pertanyaan terakhir & flag sudah terjawab
last_question_id = None
answered = False

# Event listener → tangkap balasan Elfa
@client.on(events.NewMessage(from_users=TARGET_ID))
async def handler(event):
    global last_question_id, answered

    if last_question_id is None:
        print("⚠️ last_question_id masih None → skip handler.", flush=True)
        return
    if answered:
        print("✅ Pertanyaan ini sudah terjawab, abaikan balasan tambahan.", flush=True)
        return

    print(f"[Handler] Pesan baru dari Elfa (id={event.id}), tunggu 80 detik...", flush=True)
    await asyncio.sleep(80)

    # Ambil semua pesan dari Elfa setelah pertanyaan terakhir
    responses = await client.get_messages(TARGET_ID, min_id=last_question_id, limit=10)
    print(f"[Handler] Jumlah pesan ditemukan: {len(responses)}", flush=True)

    if not responses:
        print("❌ Tidak ada balasan dari Elfa setelah pertanyaan terakhir.", flush=True)
        return

    # Pilih bubble terpanjang
    longest_msg = max(responses, key=lambda m: len(m.text or ""), default=None)

    if longest_msg and longest_msg.text:
        final_text = longest_msg.text
        print("✅ Balasan final dari Elfa (bubble terpanjang):", final_text[:120], "...", flush=True)

        payload = {"sender": "Elfa", "message": final_text}
        try:
            res = requests.post(WEBHOOK_URL, json=payload)
            print(f"[Webhook] Status: {res.status_code}", flush=True)
        except Exception as e:
            print("[Webhook] Gagal kirim:", e, flush=True)

        # Tandai sudah terjawab supaya ga dobel
        answered = True
    else:
        print("❌ Tidak ada bubble teks valid dari Elfa.", flush=True)

# Fungsi kirim pesan terjadwal
async def scheduled_message():
    global last_question_id, answered
    target = await client.get_entity(TARGET_USERNAME)
    sent = await client.send_message(
        target,
        "Berikan update news, project web3, hot topik CT hari ini, koin potensial."
    )
    last_question_id = sent.id
    answered = False  # reset flag tiap kirim pertanyaan baru
    print(f"[Scheduler] Pesan terjadwal dikirim (id={last_question_id}) @ {datetime.now()}", flush=True)

# Main loop
async def main():
    print("Menyiapkan scheduler...", flush=True)
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Jakarta"))
    scheduler.add_job(scheduled_message, "cron", hour=15, minute=39)  # 14:30 WIB
    scheduler.start()
    print("Scheduler sudah aktif, menunggu event/pesan masuk...", flush=True)

    await client.run_until_disconnected()

with client:
    print("Client Telethon connect...", flush=True)
    client.loop.run_until_complete(main())
