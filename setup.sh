#!/bin/bash

# Berhenti jika ada error
set -e

clear
echo "🌌 Nebula Userbot - Auto Installer"
echo "-----------------------------------"

# Deteksi Platform
if [ -d "/data/data/com.termux/files/usr" ]; then
    PLATFORM="termux"
    echo "📍 Platform: Termux (Android)"
else
    PLATFORM="linux"
    echo "📍 Platform: Linux VPS"
fi

# Install Dependensi Sistem
echo "📦 Installing system dependencies..."
if [ "$PLATFORM" = "termux" ]; then
    pkg update && pkg upgrade -y
    pkg install python ffmpeg aria2 openssl git clang -y
else
    sudo apt update
    sudo apt install python3 python3-pip ffmpeg aria2 git -y
fi

# Install Dependensi Python dengan verifikasi
echo "🐍 Installing python requirements..."
pip3 install --upgrade pip
if ! pip3 install -r requirements.txt; then
    echo "❌ Gagal menginstal dependensi Python. Cek koneksi atau pesan error di atas."
    exit 1
fi

# Jalankan Wizard Interaktif
echo "🧙 Memulai Wizard Persiapan..."
if ! python3 core/wizard.py; then
    echo "❌ Wizard gagal dijalankan. Pastikan library terinstal dengan benar."
    exit 1
fi

# Buat run.sh dengan logika penghentian total yang aman
cat <<EOF > run.sh
#!/bin/bash
trap "echo -e '\n🛑 \033[91mNebula Bot Berhenti Total.\033[0m'; exit" SIGINT

if ! pgrep -x \"aria2c\" > /dev/null; then
    aria2c --enable-rpc --rpc-listen-all=false --rpc-listen-port=6800 --max-connection-per-server=10 --rpc-max-request-size=100M --daemon
fi

while true; do
    python3 main.py
    if [ \$? -eq 0 ]; then
        echo -e "✅ \033[92mBot berhenti secara normal.\033[0m"
        break
    fi
    echo -e "⚠️  \033[93mBot crash/berhenti. Restarting dalam 5 detik...\033[0m"
    sleep 5
done
EOF
chmod +x run.sh

echo "-----------------------------------"
echo "✅ SEMUA BERHASIL DIINSTAL!"
echo "Gunakan './run.sh' untuk menjalankan bot kamu."
echo "-----------------------------------"
