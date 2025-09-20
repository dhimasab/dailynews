from telethon import TelegramClient

# Ganti dengan API ID dan HASH kamu
api_id = 21369351
api_hash = "290e7d6666c8cd0df296217dc9f33cab"

# Nama session file (akan bikin file lokal untuk simpan sesi login)
client = TelegramClient("n8n_session", api_id, api_hash)

async def main():
    me = await client.get_me()
    print("Login sukses sebagai:", me.username or me.first_name)

# Jalankan client
with client:
    client.loop.run_until_complete(main())
