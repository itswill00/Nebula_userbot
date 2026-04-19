from hydrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent
)


async def assistant_inline_handler(client, inline_query: InlineQuery):
    # Impor lokal untuk menghindari potensi circular import
    from .assistant import get_help_markup, get_plugin_detail_markup
    from core.decorators import CMD_HELP

    userbot = client.parent if hasattr(client, "parent") else client
    query = inline_query.query.lower().strip()

    results = []

    if not query or query == "help":
        # Menu Utama
        text = (
            "🌌 **Nebula - Help Menu**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Pilih plugin di bawah ini untuk melihat detail perintah dan pengaturan.\n"
            "Gunakan tombol `«` dan `»` untuk beralih halaman."
        )
        markup = await get_help_markup(page=0)
        results.append(
            InlineQueryResultArticle(
                title="Nebula Help Menu",
                description="Pusat Kendali & Bantuan Nebula",
                input_message_content=InputTextMessageContent(text),
                reply_markup=markup
            )
        )
    else:
        # Cek Pencarian Plugin Spesifik
        found_plugins = []
        for cat in CMD_HELP:
            for plug in CMD_HELP[cat]:
                if query in plug.lower():
                    found_plugins.append((plug, cat))

        for found_plugin, found_cat in found_plugins[:10]:  # Limit 10 hasil
            commands = CMD_HELP[found_cat][found_plugin]
            help_text = f"📦 **Plugin:** `{found_plugin.upper()}`\n"
            help_text += "━━━━━━━━━━━━━━━━━━━━\n"
            for cmd, info in commands.items():
                help_text += f"• `.{cmd}` : {info}\n"

            markup = await get_plugin_detail_markup(
                userbot, found_cat, found_plugin, 0, "ALL"
            )
            results.append(
                InlineQueryResultArticle(
                    title=f"Plugin: {found_plugin}",
                    description=f"Klik untuk bantuan {found_plugin}",
                    input_message_content=InputTextMessageContent(help_text),
                    reply_markup=markup
                )
            )

    await inline_query.answer(
        results=results,
        cache_time=1,
        is_personal=True,
        switch_pm_text="✨ Nebula Help Center",
        switch_pm_parameter="start"
    )


async def help_callback_handler(client, callback_query):
    # Ini akan dihandle oleh assistant_callback_handler di assistant.py
    # Kita biarkan kosong atau hapus jika sudah dihandle di sana
    pass
