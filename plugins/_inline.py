from hydrogram import Client, filters
from hydrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton

# Ini berjalan di Assistant Bot
# Menangani @bot_username help
@Client.on_inline_query()
async def inline_handler(client, inline_query: InlineQuery):
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
                input_message_content=InputTextMessageContent(help_text),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        ]
        await inline_query.answer(results, cache_time=1)
