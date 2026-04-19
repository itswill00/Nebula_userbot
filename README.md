# 🌌 Nebula Userbot (God Mode)

Built for speed, intelligence, and a human touch. Powered by **Hydrogram** and **Gemini 1.5 Flash**.

---

## 🚀 One-Command Installation

Run this single command on your **VPS** or **Termux** to set up everything automatically:

```bash
git clone https://github.com/itswill00/Nebula_userbot.git && cd Nebula_userbot && bash setup.sh
```

**What the installer does:**
1. Installs system dependencies (FFmpeg, Aria2, etc).
2. Sets up Python environment.
3. Launches an **Interactive Wizard** to handle your keys and Telegram login.
4. Generates a `run.sh` script for easy start/restart.

---

## 🎮 Essential Commands (Prefix: `.`)

| Command | Description |
| :--- | :--- |
| `.help` | Open the interactive help menu. |
| `.db` | Open the Dashboard to toggle features (Anti-Delete, etc). |
| `.ask` | Chat with Gemini AI. |
| `.summarize` | Get a smart summary of group chats. |
| `.vstk` | Turn video into stickers. |
| `.leech` | Download large files to VPS/Termux. |
| `.update` | Update Nebula directly from Telegram. |

---

## 🛠 Manual Deployment (Optional)

### Using Docker (Best for VPS)
1. Run the `bash setup.sh` above first to generate your session.
2. Once the wizard is finished, run:
```bash
docker-compose up -d --build
```

---

## ❤️ Your Privacy
Nebula stores your session data (`nebula.session`) and keys (`.env`) only on your local machine. These files are ignored by Git for your safety.

---
*Built with heart for a better Telegram experience.*
