# 🌌 Nebula Userbot (God Mode)

Selamat datang di **Nebula**! Ini bukan sekadar bot biasa, melainkan asisten pribadi digital yang dirancang untuk membantu kamu mengelola Telegram dengan lebih cerdas, cepat, dan tentu saja, lebih manusiawi. 

Nebula dibangun di atas fondasi **Hydrogram** yang kencang, dibekali kecerdasan **Gemini 1.5 Flash**, dan siap mendampingi kamu di berbagai platform—mulai dari VPS kelas atas sampai HP Android (Termux) kesayanganmu.

---

## ✨ Apa Saja yang Bisa Nebula Lakukan?

Nebula dibekali banyak "kekuatan" yang bisa kamu akses langsung dari chat:

- **🧠 Asisten Pintar**: Tanya apa saja atau minta ringkasan obrolan grup yang berisik lewat integrasi Gemini AI.
- **🎬 Pengolah Media**: Ubah video jadi sticker cantik atau download konten dari berbagai media sosial dalam sekejap.
- **🛡 Keamanan Ketat**: Lindungi privasi kamu dengan *PM Guard* dan pantau pesan yang dihapus orang lain secara otomatis.
- **🚀 Akses Sistem**: Kontrol server atau VPS kamu langsung dari Telegram seolah-olah kamu sedang di depan terminal.
- **🤖 Mode Asisten**: Gunakan bot asisten sebagai gerbang komunikasi agar akun utama kamu tetap bersih dari spam.

---

## 🛠 Panduan Memulai

Pilih jalur yang paling nyaman buat kamu:

### Opsi 1: Lewat Linux VPS (Paling Stabil)
Cocok buat kamu yang ingin Nebula selalu siap 24/7 tanpa henti.
1. `git clone https://github.com/itswill00/Nebula_userbot.git && cd Nebula_userbot`
2. Isi kredensial kamu di file `.env` (API ID, Hash, dll).
3. Jalankan `pip install -r requirements.txt && python3 main.py` untuk login pertama kali.
4. Setelah itu, jalankan `docker-compose up -d --build` agar dia jalan terus di latar belakang.

### Opsi 2: Lewat Termux (Di HP Android)
Praktis dan bisa dibawa ke mana saja.
1. Buka Termux, lalu ketik: `pkg install git -y`
2. Clone Nebula: `git clone https://github.com/itswill00/Nebula_userbot.git && cd Nebula_userbot`
3. Jalankan `bash setup.sh` untuk menyiapkan semuanya secara otomatis.
4. Isi file `.env`, lalu jalankan bot dengan `./run.sh`.

---

## 🎮 Perintah Favorit (Prefix: `.`)

| Perintah | Apa Gunanya? |
| :--- | :--- |
| `.help` | Buka menu bantuan yang cantik (dengan tombol!). |
| `.db` | Masuk ke Pusat Kontrol buat ganti-ganti pengaturan bot. |
| `.ask` | Tanya-tanya atau ngobrol sama AI Gemini. |
| `.summarize` | Minta ringkasan apa aja yang diomongin orang di grup. |
| `.vstk` | Bikin sticker video dari video apa aja. |
| `.leech` | Download file besar ke VPS terus kirim ke Telegram kamu. |
| `.sys` | Cek kondisi server kamu (CPU, RAM, dll) dengan bahasa santai. |
| `.update` | Update bot kamu ke versi terbaru langsung dari chat. |

---

## ⚙️ Mengatur Segalanya (`.env`)

Kamu butuh beberapa kunci buat nyalain Nebula:
- **API_ID** & **API_HASH**: Ambil di [my.telegram.org](https://my.telegram.org).
- **BOT_TOKEN**: Bikin asisten kamu di [@BotFather](https://t.me/BotFather).
- **GEMINI_API_KEY**: Kunci kecerdasan AI kamu dari [Google AI Studio](https://aistudio.google.com/).

---

## ❤️ Keamanan Kamu Utama
Nebula sangat menjaga rahasia. Semua data login kamu (`.session`) dan kunci rahasia (`.env`) tersimpan aman di perangkat kamu sendiri dan nggak akan pernah tersebar. 

## 📜 Lisensi
Nebula menggunakan Lisensi MIT. Bebas kamu pakai dan kembangkan lagi!

---
*Dibuat dengan dedikasi untuk kenyamanan kamu.*
