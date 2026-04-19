# Nebula Userbot (God Mode)

Modular MTProto Userbot yang dioptimalkan untuk performa tinggi pada Linux VPS. Memanfaatkan Hydrogram (Asyncio), Aria2 RPC untuk unduhan cepat, dan Gemini 1.5 Flash untuk integrasi AI.

## 🚀 Fitur Utama

- **Developer REPL**: Eksekusi kode Python asinkron langsung dari chat (`.eval`).
- **Network Mastery**: Uji kecepatan koneksi VPS (`.speedtest`) dan IP lookup (`.ip`).
- **Intelligence Suite**: Asisten Gemini AI, Chat Summarizer, Text-to-Speech (TTS), dan Penerjemah AI (`.tr`).
- **Media Engine**: Konversi video ke sticker (.webm) dan universal downloader (yt-dlp).
- **Leech System**: High-speed download via Aria2 RPC langsung ke Telegram.
- **Security**: PM Guard (Auto-approve), Anti-Delete/Edit logging, dan Global Ban (G-Ban).
- **Admin Tools**: Purge, Ban, Kick, Mute dengan antarmuka tombol inline (Assistant).

---

## 🛠 Panduan Instalasi Detail

### 1. Persiapan Kredensial
Sebelum memulai, siapkan data berikut:
- **API_ID & API_HASH**: Dapatkan dari [my.telegram.org](https://my.telegram.org).
- **GEMINI_API_KEY**: Dapatkan dari [Google AI Studio](https://aistudio.google.com/).
- **BOT_TOKEN**: Dapatkan dari [@BotFather](https://t.me/BotFather) (untuk fitur Assistant & Inline Button).

### 2. Persiapan VPS (Linux Ubuntu/Debian)
Update sistem dan instal Docker sebagai fondasi utama:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose git python3-pip -y
```

### 3. Clone & Konfigurasi
```bash
git clone https://github.com/itswill00/Nebula_userbot.git
cd Nebula_userbot

# Buat file konfigurasi
nano .env
```
Isi file `.env` dengan format berikut:
```env
API_ID=1234567
API_HASH=abcdef1234567890abcdef
GEMINI_API_KEY=AIzaSyA...
BOT_TOKEN=12345678:AA...
```

### 4. Autentikasi Akun (Penting)
Telegram memerlukan verifikasi OTP untuk login pertama kali. Docker berjalan di latar belakang, jadi Anda harus login secara manual satu kali:

1. Instal library pendukung sementara:
   ```bash
   pip install -r requirements.txt
   ```
2. Jalankan bot secara manual:
   ```bash
   python3 main.py
   ```
3. Ikuti instruksi di terminal:
   - Masukkan nomor telepon (`+62...`).
   - Masukkan kode OTP yang dikirim ke aplikasi Telegram Anda.
   - Masukkan password 2FA (jika ada).
4. Jika muncul pesan `Nebula Master (User) is online`, tekan **`CTRL+C`** untuk berhenti. File sesi `nebula.session` kini telah tersimpan.

### 5. Deployment Docker
Setelah file sesi terbentuk, jalankan bot secara permanen:
```bash
docker-compose up -d --build
```

---

## 🎮 Penggunaan (Prefix: `.`)

| Perintah | Deskripsi |
| :--- | :--- |
| `.help` | Menampilkan menu bantuan interaktif (Inline Button jika Assistant aktif) |
| `.db` | Membuka Dashboard Pusat Kontrol untuk menyeting fitur bot |
| `.eval <code>` | Eksekusi kode Python secara live (REPL) |
| `.sh <cmd>` | Mengeksekusi perintah shell di VPS |
| `.speedtest` | Menjalankan Speedtest jaringan VPS |
| `.vstk` | Mengubah video/GIF (reply) menjadi sticker video |
| `.leech <url>` | Download file besar via Aria2 ke Telegram |
| `.ask <teks>` | Interaksi langsung dengan Gemini AI |
| `.summarize` | Merangkum percakapan terakhir di grup |
| `.lang <id/en>` | Mengubah bahasa bot secara instan |
| `.antispam on/off`| Mengaktifkan/matikan proteksi spam otomatis |

---

## 📂 Struktur Proyek
- `core/`: Client MTProto, Database Manager, dan i18n Logic.
- `plugins/`: Modul fitur (Admin, AI, Media, Security, Dev, dll).
- `utils/`: Wrapper asinkron Shell, Aria2 RPC, dan Graphics Engine.
- `strings/`: Kamus lokalisasi bahasa (JSON).

## 🛡 Keamanan
Data sesi (`.session`) dan kredensial (`.env`) secara otomatis dikecualikan dari Git melalui `.gitignore`. **Jangan pernah membagikan file-file tersebut kepada siapapun.**

## 📜 Lisensi
Distributed under the MIT License. Lihat `LICENSE` untuk informasi lebih lanjut.
