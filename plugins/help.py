from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

PREFIX = "."

@Client.on_message(filters.command("help", prefixes=PREFIX) & filters.me)
async def help_menu(client, message: Message):
    """Dynamic help menu dengan dukungan tombol inline via Assistant."""
    
    # Header Teks
    help_text = "🌌 **Nebula Userbot God Mode**\n\nPilih kategori di bawah untuk bantuan lebih lanjut."

    # Jika Assistant aktif, kirim tombol inline
    if client.assistant:
        buttons = [
            [
                InlineKeyboardButton("System", callback_data="help_system"),
                InlineKeyboardButton("Media", callback_data="help_media")
            ],
            [
                InlineKeyboardButton("AI Tools", callback_data="help_ai"),
                InlineKeyboardButton("Security", callback_data="help_security")
            ],
            [
                InlineKeyboardButton("Settings", callback_data="help_config")
            ]
        ]
        
        # Kirim melalui Userbot memicu Assistant via InlineQuery (Cara paling efisien)
        # Atau kirim langsung jika Userbot memiliki hak admin di grup
        try:
            await message.edit(
                help_text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception:
            # Fallback jika chat tidak mendukung tombol dari Userbot langsung
            # Userbot mengirim via Bot Assistant
            bot = await client.assistant.get_me()
            await message.edit(f"{help_text}\n\n`Gunakan @{bot.username} untuk antarmuka tombol.`")
    else:
        # Fallback Text-only jika Assistant mati
        help_text += "\n\n**Commands:**\n`.sh`, `.eval`, `.vstk`, `.dl`, `.ask`, `.tr`"
        await message.edit(help_text)

# Handler Callback Button untuk Assistant
# Catatan: Ini harus dijalankan di context Assistant Bot
# Kita bisa menambahkan handler ini di file terpisah atau di sini dengan decorator yang tepat.
