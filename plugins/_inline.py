from hydrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InlineQueryResultCachedPhoto,
    InputTextMessageContent
)


async def assistant_inline_handler(client, inline_query: InlineQuery):
    # Impor lokal untuk menghindari potensi circular import
    from .assistant import get_help_markup, get_plugin_detail_markup, get_system_stats
    from core.decorators import CMD_HELP

    userbot = client.parent if hasattr(client, "parent") else client
    query = inline_query.query.lower().strip()

    results = []

    if not query or query == "help":
        # Menu Utama
        total_plugins, total_commands, addons = await get_system_stats()

        text = (
            f"Bot Of {userbot.me.first_name}@{userbot.me.username}\n\n"
            f"**Main Menu**\n\n"
            f"PLUGINS ~ {total_plugins}\n"
            f"ADDONS ~ {addons}\n"
            f"TOTAL COMMANDS ~ {total_commands}"
        )
        markup = await get_help_markup(page=0)
        
        # 1. Desain Menu Utama (Balanced HUD)
        stats = f"◈ {total_plugins} Fitur | {total_commands} Perintah"
        
        caption = (
            f"**Nebula**\n\n"
            f"`{stats}`\n"
            f"Pengguna: {userbot.me.first_name}"
        )

        # 2. Ambil Banner Acak (Shifting Cosmos)
        banner_ids = await userbot.db.get("banner_file_ids", [])
        import random
        cached_file_id = random.choice(banner_ids) if banner_ids else await userbot.db.get("banner_file_id")

        if cached_file_id:
            results.append(
                InlineQueryResultCachedPhoto(
                    photo_file_id=cached_file_id,
                    title="Nebula Menu",
                    caption=caption,
                    reply_markup=markup
                )
            )
        else:
            # Fallback ke Artikel jika cache kosong
            results.append(
                InlineQueryResultArticle(
                    title="Nebula Menu",
                    description=stats,
                    input_message_content=InputTextMessageContent(caption),
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
