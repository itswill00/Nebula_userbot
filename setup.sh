#!/bin/bash

echo "🌌 Nebula Userbot - Universal Setup"
echo "-----------------------------------"

# Deteksi Platform
if [ -d "/data/data/com.termux/files/usr" ]; then
    PLATFORM="termux"
    echo "📍 Platform: Termux (Android)"
elif [ -f "/etc/debian_version" ]; then
    PLATFORM="debian"
    echo "📍 Platform: Debian/Ubuntu"
else
    PLATFORM="linux"
    echo "📍 Platform: Generic Linux"
fi

# Install Dependensi Sistem
echo "📦 Installing system dependencies..."
if [ "$PLATFORM" = "termux" ]; then
    pkg update && pkg upgrade -y
    pkg install python ffmpeg aria2 openssl git -y
else
    sudo apt update
    sudo apt install python3 python3-pip ffmpeg aria2 git -y
fi

# Install Dependensi Python
echo "🐍 Installing python requirements..."
pip3 install -r requirements.txt

echo "-----------------------------------"
echo "✅ Setup Selesai!"
echo "Langkah selanjutnya:"
echo "1. Isi kredensial di file .env"
echo "2. Jalankan: python3 main.py"
