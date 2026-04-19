import os
import shutil
import time
from hydrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from hydrogram.errors import MessageNotModified
from core.decorators import CMD_HELP


# Konfigurasi Grid
COLUMNS = 3
ROWS = 4
PLUGINS_PER_PAGE = COLUMNS * ROWS


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


async def get_system_stats():
    """Menghitung statistik plugin dan perintah secara dinamis."""
    total_plugins = 0
    total_commands = 0
    for cat in CMD_HELP:
        total_plugins += len(CMD_HELP[cat])
        for plug in CMD_HELP[cat]:
            total_commands += len(CMD_HELP[cat][plug])

    # Hitung Addons (file .py di folder plugins yang bukan internal)
    try:
        addons = len([f for f in os.listdir("plugins") if f.endswith(".py") and not f.startswith("_")])
    except Exception:
        addons = total_plugins

    return total_plugins, total_commands, addons


# --- MARKUP GENERATORS ---

async def get_help_markup(page=0):
    """Entry point utama untuk menu bantuan (Main Menu)."""
    return await get_main_menu_markup()


async def get_main_menu_markup():
    """Halaman Awal: Menu Utama Bergaya Ultroid."""
    buttons = [
        [
            InlineKeyboardButton("Fitur", callback_data="all_plugins|0"),
            InlineKeyboardButton("Kelola", callback_data="cat|Manager|0")
        ],
        [
            InlineKeyboardButton("Keamanan", callback_data="cat|Security|0"),
            InlineKeyboardButton("Pengaturan", callback_data="cat|Config|0")
        ],
        [
            InlineKeyboardButton("Identitas", callback_data="cat|Identity|0"),
            InlineKeyboardButton("Sistem", callback_data="cat|System|0")
        ],
        [
            InlineKeyboardButton("Cari", switch_inline_query_current_chat=""),
            InlineKeyboardButton("Umum", callback_data="cat|General|0")
        ],
        [
            InlineKeyboardButton("TUTUP", callback_data="close_db")
        ]
    ]
    return InlineKeyboardMarkup(buttons)


async def get_plugin_grid_markup(category, page):
    """Grid plugin untuk kategori tertentu."""
    callback_prefix = "all_plugins" if category == "ALL" else f"cat|{category}"

    all_plugins = get_all_plugins_list()
    if category == "ALL":
        plugins = all_plugins
    else:
        plugins = sorted([p for p in all_plugins if p[1] == category])

    page_plugins, max_page = paginate_list(plugins, page)

    buttons = []
    for i in range(0, len(page_plugins), COLUMNS):
        row = [
            InlineKeyboardButton(
                p[0].title(),
                callback_data=(
                    f"pdet|{p[1]}|{p[0]}|{page}|"
                    f"{'ALL' if category == 'ALL' else category}"
                )
            )
            for p in page_plugins[i:i + COLUMNS]
        ]
        buttons.append(row)

    # Navigasi Halaman
    if max_page > 0:
        nav = []
        prev_page = page - 1 if page > 0 else max_page
        next_page = page + 1 if page < max_page else 0

        nav.append(InlineKeyboardButton(
            "Kembali", callback_data=f"{callback_prefix}|{prev_page}")
        )
        nav.append(InlineKeyboardButton(
            f"{page + 1}/{max_page + 1}", callback_data="page_info")
        )
        nav.append(InlineKeyboardButton(
            "Lanjut", callback_data=f"{callback_prefix}|{next_page}")
        )
        buttons.append(nav)
    buttons.append([
        InlineKeyboardButton("Menu Utama",
                             callback_data="back_to_main")
    ])
    return InlineKeyboardMarkup(buttons)


async def get_plugin_detail_markup(
    client_parent, category, plugin_name, back_page, back_cat
):
    """Halaman Detail Plugin."""
    buttons = []

    # Logika Kontrol
    if plugin_name == "antispam":
        state = await client_parent.db.get("antispam", False)
        cb_data = f"utog|antispam|{category}|{plugin_name}|{back_page}|{back_cat}"
        buttons.append([
            InlineKeyboardButton(
                f"Anti-Spam: {'✅ ON' if state else '❌ OFF'}",
                callback_data=cb_data
            )
        ])
    elif plugin_name == "pmpermit":
        state = await client_parent.db.get("pm_permit_enabled", True)
        cb_data = (
            f"utog|pm_permit_enabled|{category}|{plugin_name}|"
            f"{back_page}|{back_cat}"
        )
        buttons.append([
            InlineKeyboardButton(
                f"PM Permit: {'✅ ON' if state else '❌ OFF'}",
                callback_data=cb_data
            )
        ])
    elif plugin_name == "afk":
        afk_data = await client_parent.db.get("afk", {"is_afk": False})
        state = afk_data.get("is_afk")
        buttons.append([
            InlineKeyboardButton(
                f"Status: {'AFK 💤' if state else 'ONLINE ⚡'}",
                callback_data="afk_status_info"
            )
        ])
    elif plugin_name == "sudo":
        sudo_users = await client_parent.db.get("sudo_users", [])
        buttons.append([
            InlineKeyboardButton(
                f"Sudo Users: {len(sudo_users)}", callback_data="sudo_list_info")
        ])
    elif plugin_name == "system":
        lang = await client_parent.db.get("lang", "id")
        cb_data = (
            f"utog|lang_switch|{category}|{plugin_name}|{back_page}|{back_cat}"
        )
        buttons.append([
            InlineKeyboardButton(
                f"Bahasa: {lang.upper()}", callback_data=cb_data)
        ])

    back_callback = (
        f"all_plugins|{back_page}" if back_cat == "ALL"
        else f"cat|{back_cat}|{back_page}"
    )
    nav_row = [
        InlineKeyboardButton("Share", switch_inline_query=plugin_name),
        InlineKeyboardButton("Kembali", callback_data=back_callback)
    ]
    buttons.append(nav_row)
    return InlineKeyboardMarkup(buttons)


# --- HANDLERS ---

async def assistant_callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    userbot = client.parent if hasattr(client, "parent") else client

    if callback_query.from_user.id != userbot.me.id:
        return await callback_query.answer("🚫 Akses Ditolak.", show_alert=True)

    if data == "back_to_main":
        await callback_query.answer()
        try:
            await callback_query.edit_message_text(
                "**Nebula**\n"
                "Pilih bagian untuk eksplorasi fitur:",
                reply_markup=await get_main_menu_markup(),
                disable_web_page_preview=False
            )
        except MessageNotModified:
            pass

    elif data.startswith("sw_banner"):
        # sw_banner|action|msg_id
        parts = data.split("|")
        action, msg_id = parts[1], int(parts[2])
        
        await callback_query.edit_message_text("◈ Memproses visual...")
        
        try:
            # 1. Ambil pesan asli yang berisi foto
            source_msg = await client.get_messages(callback_query.message.chat.id, msg_id)
            if not (source_msg.photo or source_msg.document):
                return await callback_query.edit_message_text("❌ Media kadaluarsa.")

            # 2. Setup Folder
            banners_dir = os.path.join(os.getcwd(), "resources", "banners")
            if not os.path.exists(banners_dir):
                os.makedirs(banners_dir)

            # 3. Eksekusi Aksi
            if action == "replace":
                # Hapus semua yang ada
                for f in os.listdir(banners_dir):
                    os.remove(os.path.join(banners_dir, f))
                target_path = os.path.join(banners_dir, "cosmos.png")
            else:
                # Tambah koleksi (random name)
                target_path = os.path.join(banners_dir, f"user_{int(time.time())}.png")

            # 4. Download & Simpan
            await source_msg.download(file_name=target_path)
            
            # 5. Reset Cache Database agar visual baru langsung aktif
            await userbot.db.delete("banner_file_id")
            await userbot.db.delete("banner_file_ids")
            
            await callback_query.edit_message_text(
                "✅ **Banner Diaktifkan.**\n"
                f"Tersimpan sebagai: `{os.path.basename(target_path)}`\n\n"
                "Restart Nebula untuk memperbarui cache startup."
            )
        except Exception as e:
            await callback_query.edit_message_text(f"❌ Gagal: {e}")

    elif data.startswith("all_plugins"):
        await callback_query.answer()
        # all_plugins|page or all_plugins_page
        sep = "|" if "|" in data else "_"
        page = int(data.split(sep)[-1])
        try:
            await callback_query.edit_message_text(
                "**Fitur**\n"
                "Daftar seluruh fitur Nebula:",
                reply_markup=await get_plugin_grid_markup("ALL", page),
                disable_web_page_preview=False
            )
        except MessageNotModified:
            pass

    elif data.startswith("cat"):
        await callback_query.answer()
        sep = "|" if "|" in data else "_"
        parts = data.split(sep)
        category, page = parts[1], int(parts[2])
        try:
            await callback_query.edit_message_text(
                f"📂 **Kategori:** `{category}`\n"
                "Pilih plugin untuk detail & kontrol:",
                reply_markup=await get_plugin_grid_markup(category, page),
                disable_web_page_preview=False
            )
        except MessageNotModified:
            pass

    elif data.startswith("pdet"):
        await callback_query.answer()
        sep = "|" if "|" in data else "_"
        parts = data.split(sep)
        category, plugin_name, back_page, back_cat = (
            parts[1], parts[2], int(parts[3]), parts[4]
        )

        commands = CMD_HELP.get(category, {}).get(plugin_name, {})
        help_text = f"**Fitur:** `{plugin_name.upper()}`\n"
        help_text += "━━━━━━━━━━━━━━━\n"
        if commands:
            for cmd, info in commands.items():
                help_text += f"• `.{cmd}` : {info}\n"
        else:
            help_text += "_Tidak ada informasi perintah._"

        try:
            await callback_query.edit_message_text(
                help_text,
                reply_markup=await get_plugin_detail_markup(
                    userbot, category, plugin_name, back_page, back_cat
                ),
                disable_web_page_preview=False
            )
        except MessageNotModified:
            pass

    elif data.startswith("utog"):
        await callback_query.answer("⚡ Diupdate...")
        sep = "|" if "|" in data else "_"
        parts = data.split(sep)
        key, category, plugin_name, back_page, back_cat = (
            parts[1], parts[2], parts[3], int(parts[4]), parts[5]
        )

        if key == "lang_switch":
            curr = await userbot.db.get("lang", "id")
            await userbot.db.set("lang", "en" if curr == "id" else "id")
        else:
            curr = await userbot.db.get(key, False)
            await userbot.db.set(key, not curr)

        try:
            await callback_query.edit_message_reply_markup(
                reply_markup=await get_plugin_detail_markup(
                    userbot, category, plugin_name, back_page, back_cat
                )
            )
        except MessageNotModified:
            pass

    elif data == "close_db":
        await callback_query.answer("🗑 Menutup...")
        if callback_query.message:
            await callback_query.message.delete()
        else:
            try:
                await callback_query.edit_message_text("Tutup.")
            except MessageNotModified:
                pass

    elif data == "page_info":
        await callback_query.answer(
            "Klik Prev/Next untuk menggeser.", show_alert=True
        )

    elif data == "sudo_list_info":
        sudo_users = await userbot.db.get("sudo_users", [])
        await callback_query.answer(
            f"Daftar ID: {sudo_users}" if sudo_users else "Belum ada user sudo.",
            show_alert=True
        )

    elif data == "afk_status_info":
        await callback_query.answer(
            "Status AFK diatur via .afk", show_alert=True
        )


# --- CONTACT HANDLER ---
async def assistant_contact_handler(client, message):
    userbot = client.parent if hasattr(client, "parent") else client
    me = userbot.me

    # Handler khusus Pemilik (Manajer Visual)
    if message.from_user.id == userbot.owner_id:
        if message.photo or (message.document and message.document.mime_type and "image" in message.document.mime_type):
            return await message.reply(
                "**Sistem Visual**\n\nDetect: `Visual Baru`\nKonfigurasi sebagai banner?",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("Terapkan (Ganti)", callback_data=f"sw_banner|replace|{message.id}"),
                        InlineKeyboardButton("Tambah Koleksi", callback_data=f"sw_banner|add|{message.id}")
                    ],
                    [InlineKeyboardButton("Batalkan", callback_data="close_db")]
                ])
            )
        # Jika teks dari owner, jangan forward tapi beri respon instruksi saja
        if message.text and not message.text.startswith("."):
             return await message.reply("Gunakan menu ini untuk upload banner atau gunakan perintah userbot.")

    log_text = (
        f"📩 **Pesan Baru**\n\n"
        f"**Dari:** {message.from_user.mention} (`{message.from_user.id}`)\n"
        f"**Pesan:** {message.text or '[Media]'}"
    )
    try:
        await userbot.send_message("me", log_text)
        await message.reply("Pesan telah diteruskan.")
    except Exception:
        pass


__all__ = [
    'get_help_markup', 'get_main_menu_markup', 'assistant_callback_handler',
    'assistant_contact_handler'
]
