# Nebula Userbot (God Mode)

Modular MTProto Userbot yang dioptimalkan untuk performa tinggi pada berbagai platform. Memanfaatkan Hydrogram (Asyncio), Aria2 RPC untuk unduhan cepat, dan Gemini 1.5 Flash untuk integrasi AI.

---

## 🚀 Pilihan Instalasi

### Opsi A: Linux VPS (Rekomendasi - Docker)
Gunakan opsi ini untuk stabilitas 24/7 dan manajemen yang mudah.
1. `git clone https://github.com/itswill00/Nebula_userbot.git && cd Nebula_userbot`
2. `nano .env` (Isi kredensial)
3. `pip install -r requirements.txt && python3 main.py` (Login OTP pertama kali)
4. `docker-compose up -d --build` (Jalankan permanen)

### Opsi B: Termux (Android)
Gunakan opsi ini untuk menjalankan bot langsung dari HP Android Anda.
1. `pkg install git -y`
2. `git clone https://github.com/itswill00/Nebula_userbot.git && cd Nebula_userbot`
3. `bash setup.sh`
4. `nano .env` (Isi kredensial)
5. `python3 main.py`
*Tips: Gunakan `termux-wake-lock` agar bot tidak mati saat layar HP mati.*

### Opsi C: Local Windows / PaaS (Heroku/Railway)
Untuk Windows, pastikan Python, FFmpeg, dan Aria2 terinstal di PATH.
Untuk Heroku, cukup hubungkan repositori dan gunakan `Procfile` yang tersedia. Tambahkan buildpack Python, FFmpeg, dan Aria2.

---

## 🎮 Perintah Utama (Prefix: `.`)

| Perintah | Deskripsi |
| :--- | :--- |
| `.help` | Menu bantuan interaktif (Tombol Inline) |
| `.db` | Dashboard Pusat Kontrol (Setting Bot) |
| `.eval` | Eksekusi kode Python (REPL) |
| `.sh` | Eksekusi perintah shell / terminal |
| `.vstk` | Konversi video ke sticker video |
| `.dl` | Universal Downloader (YouTube/TikTok/dll) |
| `.leech`| Download file besar via Aria2 ke Telegram |
| `.ask` | Tanya jawab dengan Gemini AI |
| `.summarize`| Merangkum 50 pesan terakhir di grup |

---

## ⚙️ Konfigurasi Environment (`.env`)
| Variabel | Deskripsi |
| :--- | :--- |
| `API_ID` | API ID dari my.telegram.org |
| `API_HASH` | API Hash dari my.telegram.org |
| `BOT_TOKEN` | Token Assistant dari @BotFather |
| `GEMINI_API_KEY`| Key dari Google AI Studio |

---

## 🛡 Keamanan & Privasi
- Data sesi (`.session`) disimpan secara lokal dan tidak akan pernah terunggah ke Git.
- Fitur **PM Guard** melindungi Anda dari spammer di pesan pribadi.
- Fitur **G-Ban** memungkinkan Anda memblokir user nakal dari semua grup secara global.

## 📜 Lisensi
Distributed under the MIT License. Lihat `LICENSE` untuk informasi lebih lanjut.
