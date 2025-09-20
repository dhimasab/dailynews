import os
import base64
from telethon import TelegramClient

# Ambil API_ID dan API_HASH dari ENV
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

# Inisialisasi client Telethon
client = TelegramClient(session_name, api_id, api_hash)

async def main():
    me = await client.get_me()
    print("Login sukses sebagai:", me.username or me.first_name)

with client:
    client.loop.run_until_complete(main())
