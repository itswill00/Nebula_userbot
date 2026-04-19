from hydrogram.types import (
    InlineQuery,
    InlineQueryResultPhoto,
    InlineQueryResultCachedPhoto
)
from .assistant import get_banner_path


async def assistant_inline_handler(client, inline_query: InlineQuery):
    # Impor lokal untuk menghindari potensi circular import
    from .assistant import get_help_markup

    userbot = client.parent if hasattr(client, "parent") else client
    query = inline_query.query.lower()

    if query == "help":
        banner = await get_banner_path(userbot, userbot.db)
        text = (
            "🌌 **Nebula Engine - Help Menu**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Pilih plugin di bawah ini untuk melihat detail perintah dan pengaturan.\n"
            "Gunakan tombol `«` dan `»` untuk beralih halaman."
        )
        markup = await get_help_markup(page=0)

        # Cek apakah banner adalah URL publik (Catbox/Telegraph/dll)
        if isinstance(banner, str) and banner.startswith("http"):
            result = InlineQueryResultPhoto(
                photo_url=banner,
                title="Nebula Help Menu",
                description="Daftar plugin dan perintah Nebula.",
                caption=text,
                reply_markup=markup
            )

        else:
            # Jika bukan URL/Path, anggap sebagai file_id
            result = InlineQueryResultCachedPhoto(
                photo_file_id=banner,
                title="Nebula Help Menu",
                description="Daftar plugin dan perintah Nebula.",
                caption=text,
                reply_markup=markup
            )

        await inline_query.answer(
            results=[result],
            cache_time=1
        )


async def help_callback_handler(client, callback_query):
    # Ini akan dihandle oleh assistant_callback_handler di assistant.py
    # Kita biarkan kosong atau hapus jika sudah dihandle di sana
    pass
