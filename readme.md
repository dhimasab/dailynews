# 📬m Telethon DM Auto-Collector Bot

Bot ini menggunakan **Telethon** untuk **mengirim pesan otomatis ke target Telegram tertentu** pada jam terjadwal, **mengumpulkan balasan**, dan **mengirim hasilnya ke webhook eksternal** (misalnya API, Notion, Google Sheet, atau Discord).

## 🧠 Cara Kerja Bot

1. **Autentikasi otomatis:** Bot menggunakan `session` Telethon yang disimpan dalam bentuk base64 di ENV agar bisa login tanpa QR/OTP manual.
2. **Jadwal kirim pesan:** Setiap hari (atau sesuai cron) bot akan mengirim pesan berisi pertanyaan ke user target (`TARGET_USERNAME`).
3. **Menunggu balasan:** Begitu pesan dikirim, bot menunggu selama `RESPONSE_DELAY` detik untuk menerima balasan.
4. **Mengambil balasan terpanjang:** Dari seluruh balasan yang masuk setelah pesan terakhir, bot memilih teks dengan panjang terbesar (diasumsikan itu jawaban utama).
5. **Kirim ke Webhook:** Pesan balasan dikirim ke endpoint `WEBHOOK_URL` dalam format JSON.

## ⚙️ Environment Variables

| Nama ENV          | Deskripsi                                                  | Contoh                                         |
| ----------------- | ---------------------------------------------------------- | ---------------------------------------------- |
| `API_ID`          | API ID dari akun Telegram Developer                        | `123456`                                       |
| `API_HASH`        | API Hash dari akun Telegram Developer                      | `abcdef1234567890abcdef1234567890`             |
| `SESSION`         | Session Telethon dalam base64                              | *(hasil encode dari `session.session`)*        |
| `TARGET_USERNAME` | Username Telegram target                                   | `@elfa_ai`                                     |
| `TARGET_ID`       | User ID numerik target                                     | `123456789`                                    |
| `WEBHOOK_URL`     | Endpoint penerima hasil (misal Notion, Discord, Sheet API) | `https://hooks.yourapp.com/webhook`            |
| `SCHEDULE_HOUR`   | Jam pengiriman pesan (format 24 jam, WIB)                  | `9`                                            |
| `SCHEDULE_MINUTE` | Menit pengiriman pesan                                     | `30`                                           |
| `RESPONSE_DELAY`  | Waktu tunggu balasan sebelum dikirim ke webhook (detik)    | `180`                                          |
| `QUESTION_TEXT`   | Isi pertanyaan yang akan dikirim ke target                 | `Hai Elfa, bisa bantu analisis data hari ini?` |

## 🧹 Struktur File

```
.
├── main.py                # Script utama bot
├── requirements.txt       # Daftar dependensi
├── README.md              # Dokumentasi ini
└── .env                   # (opsional) file environment lokal
```

## 📦 Instalasi & Setup

1. **Clone repositori dan install dependencies:**

   ```bash
   git clone <repo-url>
   cd <repo-folder>
   pip install -r requirements.txt
   ```

2. **Buat file `.env` (opsional untuk lokal):**

   ```bash
   API_ID=123456
   API_HASH=abcdef1234567890abcdef1234567890
   SESSION=base64stringdarisession
   TARGET_USERNAME=@elfa_ai
   TARGET_ID=123456789
   WEBHOOK_URL=https://hooks.yourapp.com/webhook
   SCHEDULE_HOUR=9
   SCHEDULE_MINUTE=30
   RESPONSE_DELAY=180
   QUESTION_TEXT=Hai Elfa, bisa bantu analisis data hari ini?
   ```

3. **Jalankan bot:**

   ```bash
   python main.py
   ```

## 🕒 Alur Eksekusi

1. Saat start, bot memuat session dari ENV dan login otomatis.
2. Mengaktifkan **scheduler** (via `apscheduler`) sesuai waktu yang diatur.
3. Ketika waktu tepat:

   * Bot kirim `QUESTION_TEXT` ke `TARGET_USERNAME`.
   * Menyimpan `last_question_id`.
4. Saat target membalas:

   * Handler mencatat ID pesan.
   * Setelah `RESPONSE_DELAY`, bot mencari **pesan terpanjang** sejak `last_question_id`.
5. Mengirim hasil ke `WEBHOOK_URL` dalam format:

   ```json
   {
     "sender": "Elfa",
     "message": "Isi balasan terpanjang dari target..."
   }
   ```

## 🧮 Dependensi Utama

* `telethon` — untuk koneksi dan event Telegram.
* `apscheduler` — untuk jadwal pengiriman otomatis.
* `requests` — untuk kirim data ke webhook eksternal.
* `pytz` — untuk timezone Asia/Jakarta.
* `asyncio` — untuk manajemen event asynchronous.

## 🧼 Catatan Penting

* File session (`session.session`) **harus valid** dan dikonversi ke base64 sebelum disimpan ke ENV.
* Jangan commit file `.session` asli ke repository.
* Pastikan bot sudah pernah login sebelumnya agar tidak memerlukan OTP saat runtime.
* Waktu pengiriman menggunakan zona waktu **Asia/Jakarta (GMT+7)**.
* `RESPONSE_DELAY` terlalu pendek bisa bikin kehilangan balasan, disarankan minimal 120 detik.

## 💡 Tips Debugging

* Jika muncul error `ValueError: ENV ... wajib diisi`, berarti ENV belum di-set.
* Jika bot tidak mengirim pesan sesuai jadwal, pastikan timezone dan jam sistem benar.
* Untuk memantau event masuk, jalankan dengan log aktif:

  ```bash
  python main.py | tee logs.txt
  ```

## 📤 Contoh Output Log

```
=== Bot Telethon starting up... ===
API_ID & API_HASH loaded dari ENV. API_ID=123456
Session berhasil ditulis ke session.session
Scheduler sudah aktif @ 09:30, menunggu event/pesan masuk...
[Scheduler] Pesan terjadwal dikirim (id=2211) @ 2025-10-12 09:30:00
[Handler] Balasan pertama dari Elfa (id=2213), mulai collector...
[Collector] Jumlah pesan ditemukan: 3
✅ Balasan final dari Elfa: "Oke, aku bantu analisis hari ini ya. Kirim datanya aja~" ...
[Webhook] Status: 200
```

## 🧭 Lisensi

Proyek ini bebas digunakan untuk kebutuhan pribadi atau integrasi riset. Mohon tetap menjaga privasi target dan tidak menggunakan bot ini untuk *spam* atau aktivitas tanpa izin.
