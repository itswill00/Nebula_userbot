from hydrogram import Client
from hydrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from plugins.assistant import get_help_markup

async def assistant_inline_handler(client, inline_query: InlineQuery):
    query = inline_query.query.lower()
    
    if query == "help":
        text = (
            "🌌 **Nebula Engine - Help Menu**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Pilih plugin di bawah ini untuk melihat detail perintah dan pengaturan.\n"
            "Gunakan tombol `«` dan `»` untuk beralih halaman."
        )
        markup = await get_help_markup(page=0)
        
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    title="Nebula Help Menu",
                    input_message_content=InputTextMessageContent(text),
                    reply_markup=markup,
                    description="Daftar plugin dan perintah Nebula."
                )
            ],
            cache_time=1
        )

async def help_callback_handler(client, callback_query):
    # Ini akan dihandle oleh assistant_callback_handler di assistant.py
    # Kita biarkan kosong atau hapus jika sudah dihandle di sana
    pass
