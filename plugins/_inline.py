from hydrogram import Client, filters
from hydrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

async def assistant_inline_handler(client, inline_query: InlineQuery):
    """Menangani permintaan menu bantuan via @bot_username help."""
    query = inline_query.query.lower()
    
    if query == "help":
        help_text = "🌌 **Nebula — Pusat Kendali Kamu**\n\nHalo! Mau aku bantu apa hari ini? Pilih kategori di bawah ya."
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
        
        results = [
            InlineQueryResultArticle(
                id="help_menu",
                title="Nebula Help Menu",
                description="Pusat kontrol interaktif Nebula",
                input_message_content=InputTextMessageContent(help_text),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        ]
        await inline_query.answer(results, cache_time=1)

# --- CALLBACK HANDLER UNTUK TOMBOL HELP ---

@Client.on_callback_query(filters.regex(r"^help_"))
async def help_callback_handler(client, callback_query: CallbackQuery):
    """Menangani navigasi menu bantuan."""
    data = callback_query.data.split("_")[1]
    
    # Header berdasarkan kategori
    headers = {
        "system": "🚀 **MODUL SISTEM**\n\n• `.sh` - Eksekusi shell\n• `.sys` - Cek VPS\n• `.speedtest` - Tes koneksi\n• `.logs` - Lihat log bot",
        "media": "🎬 **MODUL MEDIA**\n\n• `.vstk` - Video ke Sticker\n• `.dl` - Downloader\n• `.leech` - High-speed Leech",
        "ai": "🧠 **MODUL AI**\n\n• `.ask` - Tanya Gemini\n• `.summarize` - Rangkum Chat\n• `.tr` - Terjemahan\n• `.tts` - Suara",
        "security": "🛡 **MODUL KEAMANAN**\n\n• `.approve` - Izin PM\n• `.gban` - Ban Global\n• `.antispam` - Anti-Spam",
        "config": "⚙️ **MODUL SETELAN**\n\n• `.db` - Dashboard\n• `.lang` - Ganti Bahasa\n• `.setting` - Atur Fitur\n• `.update` - Perbarui Bot"
    }
    
    text = headers.get(data, "Modul tidak ditemukan.")
    
    buttons = [[InlineKeyboardButton("⬅️ Kembali", callback_data="help_back")]]
    
    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("help_back"))
async def help_back_handler(client, callback_query: CallbackQuery):
    """Kembali ke menu utama bantuan."""
    help_text = "🌌 **Nebula — Pusat Kendali Kamu**\n\nHalo! Mau aku bantu apa hari ini? Pilih kategori di bawah ya."
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
    await callback_query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup(buttons))
