import os
import asyncio
from hydrogram import Client

async def run_wizard():
    print("\n" + "="*40)
    print("🌌  NEBULA USERBOT - SETUP WIZARD  🌌")
    print("="*40)
    print("\nMari siapkan Nebula kamu. Ikuti petunjuk di bawah ya!\n")

    # 1. Input Kredensial
    api_id = input("1. Masukkan API_ID: ").strip()
    api_hash = input("2. Masukkan API_HASH: ").strip()
    bot_token = input("3. Masukkan BOT_TOKEN (Assistant): ").strip()
    gemini_key = input("4. Masukkan GEMINI_API_KEY: ").strip()

    # 2. Simpan ke .env
    print("\n📝 Menyimpan konfigurasi...")
    with open(".env", "w") as f:
        f.write(f"API_ID={api_id}\n")
        f.write(f"API_HASH={api_hash}\n")
        f.write(f"BOT_TOKEN={bot_token}\n")
        f.write(f"GEMINI_API_KEY={gemini_key}\n")

    # 3. Autentikasi Telegram (Login OTP)
    print("\n🔑 Sekarang kita login ke Telegram.")
    print("   Masukkan nomor HP dan kode yang dikirim ke aplikasi Telegram kamu.\n")
    
    app = Client(
        "nebula",
        api_id=int(api_id),
        api_hash=api_hash,
        device_model="Nebula Master",
        app_version="1.3.0"
    )

    try:
        await app.start()
        me = await app.get_me()
        print(f"\n✅ Berhasil login sebagai: {me.first_name}")
        await app.stop()
        
        print("\n" + "="*40)
        print("🎉 SETUP SELESAI!")
        print("Nebula kamu siap beraksi.")
        print("="*40 + "\n")
        
    except Exception as e:
        print(f"\n❌ Login gagal: {str(e)}")
        if os.path.exists("nebula.session"):
            os.remove("nebula.session")

if __name__ == "__main__":
    asyncio.run(run_wizard())
