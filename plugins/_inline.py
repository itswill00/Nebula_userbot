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
        
        # PENTING: Inline Photo memerlukan URL Publik atau File ID.
        photo_url = userbot.banner_url
        if not photo_url.startswith("http"):
            photo_url = "https://telegra.ph/file/0c976939988a8f6022ced.jpg"

        # Tampilkan GANDA untuk stabilitas mutlak (Gaya Sentinel + Shifting Cosmos):
        # Ambil list file_id yang sudah dicache (Phase 7)
        banner_ids = await userbot.db.get("banner_file_ids", [])
        
        # Pilih secara acak jika ada (Shifting Cosmos)
        if banner_ids:
            import random
            cached_file_id = random.choice(banner_ids)
        else:
            # Fallback ke cache tunggal jika list kosong
            cached_file_id = await userbot.db.get("banner_file_id")

        if cached_file_id:
            # PRIORITAS 1: Foto dari Cache Server (100% Stabil & Cepat)
            results.append(
                InlineQueryResultCachedPhoto(
                    photo_file_id=cached_file_id,
                    title="Nebula Dashboard (Premium)",
                    caption=text,
                    reply_markup=markup
                )
            )
        else:
            # PRIORITAS 2: Hasil Foto via URL (Hanya jika cache kosong)
            results.append(
                InlineQueryResultPhoto(
                    photo_url=photo_url,
                    thumb_url=photo_url,
                    title="Nebula Dashboard (Premium)",
                    caption=text,
                    reply_markup=markup
                )
            )
        
        # 3. Hasil Artikel (Pasti Berhasil / Safe Mode)
        results.append(
            InlineQueryResultArticle(
                title="Nebula Help Center (Safe Mode)",
                description="Buka menu bantuan jika gambar gagal muncul.",
                input_message_content=InputTextMessageContent(text),
                reply_markup=markup,
                thumb_url=photo_url
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
