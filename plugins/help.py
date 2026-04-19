from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from hydrogram.errors import PeerIdInvalid, FloodWait
import asyncio

PREFIX = "."

@Client.on_message(filters.command("help", prefixes=PREFIX) & filters.me)
async def help_menu(client, message: Message):
    """Menampilkan menu bantuan interaktif atau teks fallback."""
    
    help_text = (
        "🌌 **Nebula — Pusat Kendali Kamu**\n\n"
        "Halo! Mau aku bantu apa hari ini? Pilih kategori di bawah ya."
    )

    # Persiapkan tombol
    buttons = [
        [
            InlineKeyboardButton("🚀 Sistem", callback_data="help_system"),
            InlineKeyboardButton("🎬 Media", callback_data="help_media")
        ],
        [
            InlineKeyboardButton("🧠 AI Tools", callback_data="help_ai"),
            InlineKeyboardButton("🛡 Keamanan", callback_data="help_security")
        ],
        [
            InlineKeyboardButton("⚙️ Setelan", callback_data="help_config")
        ]
    ]

    # Jika Assistant tidak aktif, kirim teks biasa
    if not client.assistant:
        return await message.edit(
            f"{help_text}\n\n**Perintah:** `.sh`, `.eval`, `.vstk`, `.dl`, `.ask`, `.db`"
        )

    try:
        # Coba kirim via Assistant Bot (untuk tombol)
        await client.assistant.send_message(
            chat_id=message.chat.id,
            text=help_text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        # Jika berhasil, hapus pesan pemicu (.help)
        await message.delete()
        
    except (PeerIdInvalid, Exception):
        # Fallback: Jika bot tidak ada di grup/chat, gunakan teks biasa melalui Userbot
        fallback_text = (
            f"{help_text}\n\n"
            "⚠️ **Catatan:** Tombol interaktif nggak muncul karena aku (Bot Assistant) belum ada di chat ini.\n\n"
            "**Daftar Perintah:**\n"
            "• `Sistem`: `.sh`, `.eval`, `.sys`, `.speedtest`\n"
            "• `Media`: `.vstk`, `.dl`, `.leech`\n"
            "• `AI`: `.ask`, `.summarize`, `.tr`, `.tts`\n"
            "• `Admin`: `.purge`, `.ban`, `.mute`, `.gban`"
        )
        await message.edit(fallback_text)
