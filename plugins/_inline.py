from hydrogram.types import (
    InlineQuery,
    InlineQueryResultPhoto
)
from .assistant import get_banner_path


async def assistant_inline_handler(client, inline_query: InlineQuery):
    # Impor lokal untuk menghindari potensi circular import
    from .assistant import get_help_markup

    userbot = client.parent if hasattr(client, "parent") else client
    query = inline_query.query.lower()

    if query == "help":
        banner = await get_banner_path(userbot.db)
        text = (
            "🌌 **Nebula Engine - Help Menu**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Pilih plugin di bawah ini untuk melihat detail perintah dan pengaturan.\n"
            "Gunakan tombol `«` dan `»` untuk beralih halaman."
        )
        markup = await get_help_markup(page=0)

        await inline_query.answer(
            results=[
                InlineQueryResultPhoto(
                    photo_url=banner,
                    title="Nebula Help Menu",
                    description="Daftar plugin dan perintah Nebula.",
                    caption=text,
                    reply_markup=markup
                )
            ],
            cache_time=1
        )


async def help_callback_handler(client, callback_query):
    # Ini akan dihandle oleh assistant_callback_handler di assistant.py
    # Kita biarkan kosong atau hapus jika sudah dihandle di sana
    pass
