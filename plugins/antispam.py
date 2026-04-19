import time
from hydrogram import Client, filters
from hydrogram.types import Message, ChatPermissions

# Dictionary in-memory untuk melacak aktivitas (user_id: [timestamps])
SPAM_TRACKER = {}
# Konfigurasi: 5 pesan dalam 8 detik dianggap spam
MSG_LIMIT = 5
TIME_WINDOW = 8

@Client.on_message(filters.group & ~filters.me & ~filters.bot, group=-3)
async def detect_spam(client, message: Message):
    """Mendeteksi pengiriman pesan cepat dan memberikan tindakan Mute."""
    is_antispam_on = await client.db.get("antispam", False)
    if not is_antispam_on:
        return

    user_id = message.from_user.id
    current_time = time.time()
    
    if user_id not in SPAM_TRACKER:
        SPAM_TRACKER[user_id] = []
    
    # Tambah timestamp pesan baru
    SPAM_TRACKER[user_id].append(current_time)
    
    # Bersihkan timestamps yang sudah di luar jendela waktu
    SPAM_TRACKER[user_id] = [t for t in SPAM_TRACKER[user_id] if current_time - t < TIME_WINDOW]
    
    if len(SPAM_TRACKER[user_id]) > MSG_LIMIT:
        try:
            # Mute user selama 1 jam
            await client.restrict_chat_member(
                message.chat.id, 
                user_id, 
                ChatPermissions(can_send_messages=False),
                until_date=int(current_time + 3600)
            )
            await message.reply(f"🔇 **Spam Detected!**\nUser `{user_id}` telah di-mute selama 1 jam.")
            # Hapus histori agar tidak terpicu lagi segera
            SPAM_TRACKER[user_id] = []
        except Exception:
            pass # Bot mungkin tidak punya akses admin

@Client.on_message(filters.command("antispam", prefixes=".") & filters.me)
async def toggle_antispam(client, message: Message):
    """Mengaktifkan atau menonaktifkan fitur anti-spam."""
    if len(message.command) < 2:
        return await message.edit("`Gunakan .antispam on/off`")
    
    state = message.command[1].lower() == "on"
    await client.db.set("antispam", state)
    await message.edit(f"🛡 **Anti-Spam Engine:** `{'ON' if state else 'OFF'}`")
