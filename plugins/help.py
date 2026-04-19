from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

PREFIX = "."

@Client.on_message(filters.command("help", prefixes=PREFIX) & filters.me)
async def help_menu(client, message: Message):
    """Menampilkan menu bantuan interaktif via Assistant Bot."""
    
    # Jika Assistant tidak aktif, tampilkan teks biasa
    if not client.assistant:
        help_text = (
            "🌌 **Nebula Userbot (Text Mode)**\n\n"
            "**Commands:**\n"
            "`.sh`, `.eval`, `.sys`, `.vstk`, `.dl`, `.leech`, `.ask`, `.tr`, `.db`"
        )
        return await message.edit(help_text)

    # Persiapkan tombol
    buttons = [
        [
            InlineKeyboardButton("🚀 System", callback_data="help_system"),
            InlineKeyboardButton("🎬 Media", callback_data="help_media")
        ],
        [
            InlineKeyboardButton("🧠 AI Tools", callback_data="help_ai"),
            InlineKeyboardButton("🛡 Security", callback_data="help_security")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="help_config")
        ]
    ]

    try:
        # 1. Hapus pesan perintah (.help)
        await message.delete()
        
        # 2. Perintah Assistant Bot untuk kirim pesan baru dengan tombol
        # Kita gunakan send_message dari client.assistant
        await client.assistant.send_message(
            chat_id=message.chat.id,
            text="🌌 **Nebula — Pusat Kendali Kamu**\n\nHalo! Mau aku bantu apa hari ini? Pilih kategori di bawah ya.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        # Fallback jika bot belum masuk grup atau belum di-start di PM
        bot_info = await client.assistant.get_me()
        await client.send_message(
            message.chat.id,
            f"❌ **Assistant Bot Error:**\n`{str(e)}`\n\nPastikan kamu sudah klik /start di @{bot_info.username}"
        )
