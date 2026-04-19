# 🌌 Nebula Userbot (God Mode)

Welcome to **Nebula**! This is not just another userbot; it's your personal digital assistant designed to help you manage Telegram smarter, faster, and more naturally.

Built on the high-performance **Hydrogram** framework and powered by **Gemini 1.5 Flash** AI, Nebula is ready to accompany you on any platform—from high-end VPS to your Android phone (Termux).

---

## ✨ Features at a Glance

- **🧠 Smart AI Assistant**: Chat with Gemini AI or get instant summaries of long group conversations.
- **🎬 Media Master**: Convert videos to stickers (.webm) or download content from any social media.
- **🛡 Rock-Solid Security**: Protect your privacy with *PM Guard* and track deleted/edited messages.
- **🚀 System Access**: Execute shell commands or monitor your VPS performance directly from chat.
- **🤖 Dual-Client Interface**: An optional Assistant Bot provides a beautiful inline button interface.

---

## 🚀 Quick Start (Copy & Paste)

Choose your platform and run the commands below.

### Option A: Linux VPS (Docker - Recommended)
Best for 24/7 stability.
```bash
git clone https://github.com/itswill00/Nebula_userbot.git && cd Nebula_userbot
# 1. Edit your credentials
nano .env
# 2. Login once to generate session
pip install -r requirements.txt && python3 main.py
# 3. Run permanently
docker-compose up -d --build
```

### Option B: Android (Termux)
Run Nebula directly from your phone.
```bash
pkg install git -y && git clone https://github.com/itswill00/Nebula_userbot.git && cd Nebula_userbot
# 1. Run automated setup
bash setup.sh
# 2. Edit your credentials
nano .env
# 3. Start the bot
./run.sh
```

---

## 🎮 Essential Commands (Prefix: `.`)

| Command | Description |
| :--- | :--- |
| `.help` | Opens a beautiful, interactive help menu. |
| `.db` | Opens the Control Center dashboard for easy settings. |
| `.ask` | Chat directly with Gemini AI. |
| `.summarize` | Get a smart summary of recent group chats. |
| `.vstk` | Turn any video into a high-quality video sticker. |
| `.leech` | Download large files to VPS and upload to Telegram. |
| `.sys` | Monitor your server status with a friendly report. |
| `.update` | Update Nebula to the latest version via chat. |

---

## ⚙️ Configuration (`.env`)

You'll need these keys to power up Nebula:
- **API_ID** & **API_HASH**: Get them at [my.telegram.org](https://my.telegram.org).
- **BOT_TOKEN**: Create your assistant at [@BotFather](https://t.me/BotFather).
- **GEMINI_API_KEY**: Get your AI key at [Google AI Studio](https://aistudio.google.com/).

---

## ❤️ Your Privacy Matters
Nebula is designed with security in mind. Your session data (`.session`) and secret keys (`.env`) are stored locally on your device and are never shared or uploaded.

## 📜 License
Distributed under the MIT License. Feel free to use and modify!

---
*Built with heart for a better Telegram experience.*
