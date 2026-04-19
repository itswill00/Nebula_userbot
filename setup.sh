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

# Buat script launcher dengan auto-restart
echo "🚀 Creating auto-restart launcher..."
cat <<EOF > run.sh
#!/bin/bash
aria2c --enable-rpc --rpc-listen-all=false --rpc-listen-port=6800 --max-connection-per-server=10 --rpc-max-request-size=100M --daemon
while true; do
    echo "Starting Nebula Userbot..."
    python3 main.py
    echo "Bot stopped/restarting in 5 seconds..."
    sleep 5
done
EOF
chmod +x run.sh

echo "-----------------------------------"
echo "✅ Setup Selesai!"
echo "Langkah selanjutnya:"
echo "1. Isi kredensial di file .env"
echo "2. Jalankan bot dengan: ./run.sh"
