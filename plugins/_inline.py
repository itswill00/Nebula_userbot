from hydrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent
)
from .assistant import get_banner_path


async def assistant_inline_handler(client, inline_query: InlineQuery):
    # Impor lokal untuk menghindari potensi circular import
    from .assistant import get_help_markup

    userbot = client.parent if hasattr(client, "parent") else client
    query = inline_query.query.lower()

    if query == "help":
        banner = await get_banner_path(userbot, userbot.db)
        # Gunakan format invisible link agar gambar muncul di link preview
        # \xad adalah soft hyphen, hampir tidak terlihat.
        text = (
            f"[\xad]({banner})🌌 **Nebula Engine - Help Menu**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Pilih plugin di bawah ini untuk melihat detail perintah dan pengaturan.\n"
            "Gunakan tombol `«` dan `»` untuk beralih halaman."
        )
        markup = await get_help_markup(page=0)

        result = InlineQueryResultArticle(
            title="Nebula Help Menu",
            description="Daftar plugin dan perintah Nebula.",
            input_message_content=InputTextMessageContent(
                message_text=text,
                disable_web_page_preview=False
            ),
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
