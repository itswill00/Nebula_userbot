#!/bin/bash
# Tangkap Ctrl+C (SIGINT) agar benar-benar berhenti
trap "echo -e '\n🛑 \033[91mNebula Bot Berhenti Total.\033[0m'; exit" SIGINT

# Nyalakan aria2c di background (jika belum nyala)
if ! pgrep -x "aria2c" > /dev/null; then
    aria2c --enable-rpc --rpc-listen-all=false --rpc-listen-port=6800 --max-connection-per-server=10 --rpc-max-request-size=100M --daemon
fi

while true; do
    python3 main.py
    # Jika Python keluar dengan kode 0 (normal exit), kita berhenti
    # Tapi jika Python crash, kita tunggu 5 detik lalu restart
    if [ $? -eq 0 ]; then
        echo -e "✅ \033[92mBot berhenti secara normal.\033[0m"
        break
    fi
    echo -e "⚠️  \033[93mBot crash/berhenti. Restarting dalam 5 detik...\033[0m"
    echo "Tekan Ctrl+C lagi untuk berhenti total."
    sleep 5
done
