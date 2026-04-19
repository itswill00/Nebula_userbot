# Nebula Userbot (God Mode)

Modular MTProto Userbot yang dioptimalkan untuk performa tinggi pada Linux VPS. Memanfaatkan Hydrogram (Asyncio), Aria2 RPC untuk unduhan cepat, dan Gemini 1.5 Flash untuk integrasi AI.

## Fitur Utama Terkini

- **Developer REPL**: Eksekusi kode Python asinkron langsung dari chat (`.eval`).
- **Network Mastery**: Uji kecepatan koneksi VPS (`.speedtest`) dan IP lookup (`.ip`).
- **Intelligence Suite**: Asisten Gemini AI, Chat Summarizer, Text-to-Speech (TTS), dan Penerjemah AI (`.tr`).
- **Media Engine**: Konversi video ke sticker (.webm) dan universal downloader (yt-dlp).
- **Leech System**: High-speed download via Aria2 RPC langsung ke Telegram.
- **Security**: PM Guard (Auto-approve) dan Anti-Delete/Edit logging.
- **Admin Tools**: Purge, Ban, Kick, Mute dengan optimasi bulk operation.

## Persiapan Sistem

- Python 3.10+
- Docker & Docker Compose
- Telegram API ID & Hash ([my.telegram.org](https://my.telegram.org))
- Google AI API Key ([Google AI Studio](https://aistudio.google.com/))

## Instalasi

1. **Clone Repositori**
   ```bash
   git clone https://github.com/itswill00/Nebula_userbot.git
   cd Nebula_userbot
   ```

2. **Konfigurasi Environment**
   Salin `.env.sample` atau buat file `.env`:
   ```env
   API_ID=123456
   API_HASH=abcdef1234567890
   GEMINI_API_KEY=your_gemini_key
   ```

3. **Login Akun (Pertama Kali)**
   Jalankan secara lokal untuk men-generate file sesi (`nebula.session`):
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

4. **Deployment via Docker**
   ```bash
   docker-compose up -d --build
   ```

## Perintah Utama (Prefix: `.`)

| Perintah | Deskripsi |
| :--- | :--- |
| `.help` | Menampilkan menu bantuan dinamis |
| `.eval <code>` | Eksekusi kode Python secara live (REPL) |
| `.sh <cmd>` | Mengeksekusi perintah shell di VPS |
| `.speedtest` | Menjalankan Speedtest CLI di VPS |
| `.ip [ip]` | Mencari detail lokasi dan ISP dari IP |
| `.vstk` | Mengubah video/GIF (reply) menjadi sticker video |
| `.dl <url>` | Download media universal ke Telegram |
| `.leech <url>` | Download file besar via Aria2 ke Telegram |
| `.ask <teks>` | Interaksi langsung dengan Gemini AI |
| `.tr <lang>` | Penerjemah cerdas (Gemini AI) |
| `.tts <teks>` | Mengubah teks menjadi Voice Note |
| `.weather <kota>`| Info cuaca real-time |

## Struktur Proyek

- `core/`: Client MTProto dan manajemen Database (JSON).
- `plugins/`: Modul fitur (Admin, AI, Media, System, Network, Dev, dll).
- `utils/`: Wrapper asinkron untuk Shell, Aria2, dan FFmpeg.
- `downloads/`: Direktori sementara untuk pemrosesan file.

## Lisensi
Distributed under the MIT License. Lihat `LICENSE` untuk informasi lebih lanjut.
