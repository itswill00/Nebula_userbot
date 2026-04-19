from hydrogram import Client
from hydrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton

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
