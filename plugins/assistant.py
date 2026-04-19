from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from core.decorators import CMD_HELP


# Konfigurasi Grid
COLUMNS = 3
ROWS = 4
PLUGINS_PER_PAGE = COLUMNS * ROWS
DEFAULT_BANNER = "resources/banner.jpg"


async def get_banner_path(db):
    """Ambil path banner dari database atau gunakan default."""
    return await db.get("help_banner", DEFAULT_BANNER)


# --- DATA HELPERS ---

def get_all_plugins_list():
    """Ambil semua plugin dari semua kategori dalam satu list flat."""
    all_plugins = []
    for cat in CMD_HELP:
        for plug in CMD_HELP[cat]:
            if (plug, cat) not in all_plugins:
                all_plugins.append((plug, cat))
    return sorted(all_plugins)


def paginate_list(items, page):
    """Membagi list ke dalam halaman."""
    start = page * PLUGINS_PER_PAGE
    stop = start + PLUGINS_PER_PAGE
    return items[start:stop], (len(items) - 1) // PLUGINS_PER_PAGE


# --- MARKUP GENERATORS ---

async def get_help_markup(page=0):
    """Entry point utama untuk menu bantuan (Main Menu)."""
    return await get_main_menu_markup()


async def get_main_menu_markup():
    """Halaman Awal: Menu Utama Bergaya Ultroid."""
    buttons = [
        [
            InlineKeyboardButton("🛠️ Utilities", callback_data="all_plugins_0"),
            InlineKeyboardButton("🛡️ Security", callback_data="cat_Security_0")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="cat_Config_0"),
            InlineKeyboardButton("👤 Identity", callback_data="cat_Identity_0")
        ],
        [
            InlineKeyboardButton("🖼️ Ganti Banner", callback_data="change_banner"),
            InlineKeyboardButton("🗑 Tutup Menu", callback_data="close_db")
        ]
    ]
    return InlineKeyboardMarkup(buttons)


async def get_plugin_grid_markup(category, page):
    """Grid plugin untuk kategori tertentu."""
    if category == "ALL":
        plugins = get_all_plugins_list()
        callback_prefix = "all_plugins"
    else:
        plugins = [(p, category) for p in sorted(CMD_HELP.get(category, {}).keys())]
        callback_prefix = f"cat_{category}"

    page_plugins, max_page = paginate_list(plugins, page)

    buttons = []
    for i in range(0, len(page_plugins), COLUMNS):
        row = [
            InlineKeyboardButton(
                p[0].title(),
                callback_data=f"pdet_{p[1]}_{p[0]}_{page}_{'ALL' if category == 'ALL' else category}"
            )
            for p in page_plugins[i:i+COLUMNS]
        ]
        buttons.append(row)

    # Navigasi Halaman
    nav = []
    prev_page = page - 1 if page > 0 else max_page
    next_page = page + 1 if page < max_page else 0

    nav.append(InlineKeyboardButton("« Prev", callback_data=f"{callback_prefix}_{prev_page}"))
    nav.append(InlineKeyboardButton(f"{page+1}/{max_page+1}", callback_data="page_info"))
    nav.append(InlineKeyboardButton("Next »", callback_data=f"{callback_prefix}_{next_page}"))

    buttons.append(nav)
    buttons.append([InlineKeyboardButton("⬅️ Kembali ke Menu", callback_data="back_to_main")])
    return InlineKeyboardMarkup(buttons)


async def get_plugin_detail_markup(client_parent, category, plugin_name, back_page, back_cat):
    """Halaman Detail Plugin."""
    buttons = []

    # Logika Kontrol
    if plugin_name == "antispam":
        state = await client_parent.db.get("antispam", False)
        cb_data = f"utog_antispam_{category}_{plugin_name}_{back_page}_{back_cat}"
        buttons.append([InlineKeyboardButton(f"Anti-Spam: {'✅ ON' if state else '❌ OFF'}", callback_data=cb_data)])
    elif plugin_name == "pmpermit":
        state = await client_parent.db.get("pm_permit_enabled", True)
        cb_data = f"utog_pm_permit_enabled_{category}_{plugin_name}_{back_page}_{back_cat}"
        buttons.append([InlineKeyboardButton(f"PM Permit: {'✅ ON' if state else '❌ OFF'}", callback_data=cb_data)])
    elif plugin_name == "afk":
        afk_data = await client_parent.db.get("afk", {"is_afk": False})
        state = afk_data.get("is_afk")
        buttons.append([
            InlineKeyboardButton(
                f"Status: {'AFK 💤' if state else 'ONLINE ⚡'}",
                callback_data="afk_status_info"
            )
        ])
    elif plugin_name == "system":
        lang = await client_parent.db.get("lang", "id")
        cb_data = f"utog_lang_switch_{category}_{plugin_name}_{back_page}_{back_cat}"
        buttons.append([InlineKeyboardButton(f"Bahasa: {lang.upper()}", callback_data=cb_data)])

    back_callback = f"all_plugins_{back_page}" if back_cat == "ALL" else f"cat_{back_cat}_{back_page}"
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data=back_callback)])
    return InlineKeyboardMarkup(buttons)


# --- HANDLERS ---

async def assistant_callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    userbot = client.parent if hasattr(client, "parent") else client

    if callback_query.from_user.id != userbot.me.id:
        return await callback_query.answer("🚫 Akses Ditolak.", show_alert=True)

    if data == "back_to_main":
        await callback_query.answer()
        await callback_query.edit_message_caption(
            "🌌 **Nebula Engine - Help Menu**\nPilih kategori untuk menjelajahi plugin:",
            reply_markup=await get_main_menu_markup()
        )

    elif data == "change_banner":
        await callback_query.answer()
        await userbot.db.set("waiting_for_banner", True)
        await callback_query.edit_message_caption(
            "🖼️ **Ganti Banner Help Menu**\n\n"
            "Silakan kirimkan sebuah **Foto** ke bot ini untuk dijadikan banner baru.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Batal", callback_data="back_to_main")]])
        )

    elif data.startswith("all_plugins_"):
        await callback_query.answer()
        page = int(data.split("_")[-1])
        await callback_query.edit_message_caption(
            "🛠 **All Utilities**\nGeser ke kiri/kanan untuk melihat semua plugin:",
            reply_markup=await get_plugin_grid_markup("ALL", page)
        )

    elif data.startswith("cat_"):
        await callback_query.answer()
        _, category, page = data.split("_")
        page = int(page)
        await callback_query.edit_message_caption(
            f"📂 **Kategori:** `{category}`\nPilih plugin untuk detail & kontrol:",
            reply_markup=await get_plugin_grid_markup(category, page)
        )

    elif data.startswith("pdet_"):
        await callback_query.answer()
        parts = data.split("_")
        category, plugin_name, back_page, back_cat = (
            parts[1], parts[2], int(parts[3]), parts[4]
        )

        commands = CMD_HELP.get(category, {}).get(plugin_name, {})
        help_text = f"📦 **Plugin:** `{plugin_name.upper()}`\n"
        help_text += "━━━━━━━━━━━━━━━━━━━━\n"
        if commands:
            for cmd, info in commands.items():
                help_text += f"• `.{cmd}` : {info}\n"
        else:
            help_text += "_Tidak ada informasi perintah._"

        await callback_query.edit_message_caption(
            help_text,
            reply_markup=await get_plugin_detail_markup(
                userbot, category, plugin_name, back_page, back_cat
            )
        )

    elif data.startswith("utog_"):
        await callback_query.answer("⚡ Diupdate...")
        parts = data.split("_")
        key, category, plugin_name, back_page, back_cat = parts[1], parts[2], parts[3], int(parts[4]), parts[5]

        if key == "lang_switch":
            curr = await userbot.db.get("lang", "id")
            await userbot.db.set("lang", "en" if curr == "id" else "id")
        else:
            curr = await userbot.db.get(key, False)
            await userbot.db.set(key, not curr)

        await callback_query.edit_message_reply_markup(
            reply_markup=await get_plugin_detail_markup(userbot, category, plugin_name, back_page, back_cat)
        )

    elif data == "close_db":
        await callback_query.answer("🗑 Menutup...")
        await callback_query.message.delete()

    elif data == "page_info":
        await callback_query.answer("Klik Prev/Next untuk menggeser.", show_alert=True)

    elif data == "afk_status_info":
        await callback_query.answer("Status AFK diatur via .afk", show_alert=True)


# --- CONTACT HANDLER ---
async def assistant_contact_handler(client, message: Message):
    userbot = client.parent if hasattr(client, "parent") else client
    me = userbot.me

    # Cek apakah ini pesan dari owner untuk ganti banner
    if message.from_user.id == me.id:
        if await userbot.db.get("waiting_for_banner"):
            if message.photo:
                await userbot.db.set("help_banner", message.photo.file_id)
                await userbot.db.delete("waiting_for_banner")
                return await message.reply("✅ **Banner Help Menu berhasil diperbarui!**")
            elif message.text == "/cancel" or message.text == "Batal":
                await userbot.db.delete("waiting_for_banner")
                return await message.reply("❌ **Penggantian banner dibatalkan.**")

    if message.from_user.id == me.id:
        return

    log_text = (
        f"📩 **Pesan Baru di Assistant Bot**\n\n"
        f"**Dari:** {message.from_user.mention} (`{message.from_user.id}`)\n"
        f"**Pesan:** {message.text or '[Media]'}"
    )
    try:
        await userbot.send_message("me", log_text)
        await message.reply("✅ Pesan kamu telah diteruskan ke Bos saya.")
    except Exception:
        pass


__all__ = [
    'get_help_markup', 'get_main_menu_markup', 'assistant_callback_handler',
    'assistant_contact_handler', 'get_banner_path'
]
