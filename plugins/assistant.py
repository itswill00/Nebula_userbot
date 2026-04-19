import os
from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from core.decorators import on_cmd, CMD_HELP

# Konfigurasi Grid
COLUMNS = 3
ROWS = 4
PLUGINS_PER_PAGE = COLUMNS * ROWS

# --- DATA HELPERS ---

def get_plugins_by_category(category):
    """Ambil daftar plugin di bawah kategori tertentu."""
    if category not in CMD_HELP:
        return []
    return sorted(CMD_HELP[category].keys())

def paginate_plugins(plugins, page):
    """Membagi plugin ke dalam halaman."""
    start = page * PLUGINS_PER_PAGE
    stop = start + PLUGINS_PER_PAGE
    return plugins[start:stop], (len(plugins) - 1) // PLUGINS_PER_PAGE

# --- MARKUP GENERATORS ---

async def get_main_menu_markup():
    """Halaman Awal: Pilih Kategori."""
    categories = sorted(CMD_HELP.keys())
    buttons = []
    # Buat grid kategori (2 kolom)
    for i in range(0, len(categories), 2):
        row = []
        for cat in categories[i:i+2]:
            count = len(CMD_HELP[cat])
            row.append(InlineKeyboardButton(f"📁 {cat} ({count})", callback_data=f"cat_{cat}_0"))
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton("🗑 Tutup Menu", callback_data="close_db")])
    return InlineKeyboardMarkup(buttons)

async def get_plugin_grid_markup(category, page):
    """Halaman Grid Plugin: Daftar Plugin dalam Kategori dengan Pagination."""
    plugins = get_plugins_by_category(category)
    page_plugins, max_page = paginate_plugins(plugins, page)
    
    buttons = []
    # Buat Grid Plugin
    for i in range(0, len(page_plugins), COLUMNS):
        row = [
            InlineKeyboardButton(p.title(), callback_data=f"pdet_{category}_{p}_{page}") 
            for p in page_plugins[i:i+COLUMNS]
        ]
        buttons.append(row)
    
    # Tombol Navigasi Halaman
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("« Prev", callback_data=f"cat_{category}_{page-1}"))
    else:
        nav.append(InlineKeyboardButton("« End", callback_data=f"cat_{category}_{max_page}"))
        
    nav.append(InlineKeyboardButton(f"{page+1}/{max_page+1}", callback_data="page_info"))
    
    if page < max_page:
        nav.append(InlineKeyboardButton("Next »", callback_data=f"cat_{category}_{page+1}"))
    else:
        nav.append(InlineKeyboardButton("First »", callback_data=f"cat_{category}_0"))
    
    buttons.append(nav)
    buttons.append([InlineKeyboardButton("⬅️ Kembali ke Menu", callback_data="back_to_main")])
    return InlineKeyboardMarkup(buttons)

async def get_plugin_detail_markup(client_parent, category, plugin_name, back_page):
    """Halaman Detail: Info Perintah + Tombol Kontrol Plugin."""
    buttons = []
    
    # LOGIKA KONTROL: Tambahkan tombol toggle jika plugin memiliki state di DB
    # Kita buat pemetaan manual berdasarkan plugin yang kita tahu punya kontrol
    if plugin_name == "antispam":
        state = await client_parent.db.get("antispam", False)
        buttons.append([InlineKeyboardButton(f"Anti-Spam: {'✅ ON' if state else '❌ OFF'}", callback_data=f"utog_antispam_{category}_{plugin_name}_{back_page}")])
    elif plugin_name == "pmpermit":
        state = await client_parent.db.get("pm_permit_enabled", True)
        buttons.append([InlineKeyboardButton(f"PM Permit: {'✅ ON' if state else '❌ OFF'}", callback_data=f"utog_pm_permit_enabled_{category}_{plugin_name}_{back_page}")])
    elif plugin_name == "afk":
        afk_data = await client_parent.db.get("afk", {"is_afk": False})
        buttons.append([InlineKeyboardButton(f"Status: {'AFK 💤' if afk_data.get('is_afk') else 'ONLINE ⚡'}", callback_data="afk_status_info")])
    elif plugin_name == "system":
        lang = await client_parent.db.get("lang", "id")
        buttons.append([InlineKeyboardButton(f"Bahasa: {lang.upper()}", callback_data=f"utog_lang_switch_{category}_{plugin_name}_{back_page}")])

    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data=f"cat_{category}_{back_page}")])
    return InlineKeyboardMarkup(buttons)

# --- HANDLERS ---

async def assistant_callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    userbot = client.parent if hasattr(client, "parent") else client
    
    if callback_query.from_user.id != userbot.me.id:
        return await callback_query.answer("🚫 Akses Ditolak.", show_alert=True)

    # 1. Menu Utama
    if data == "back_to_main":
        await callback_query.answer()
        await callback_query.edit_message_text(
            "🌌 **Nebula Engine - Help Menu**\nPilih kategori untuk menjelajahi plugin:",
            reply_markup=await get_main_menu_markup()
        )

    # 2. Grid Plugin (Categorized + Paginated)
    elif data.startswith("cat_"):
        await callback_query.answer()
        _, category, page = data.split("_")
        page = int(page)
        text = f"📂 **Kategori:** `{category}`\nPilih plugin untuk detail & kontrol:"
        await callback_query.edit_message_text(text, reply_markup=await get_plugin_grid_markup(category, page))

    # 3. Detail Plugin
    elif data.startswith("pdet_"):
        await callback_query.answer()
        _, category, plugin_name, back_page = data.split("_")
        
        commands = CMD_HELP.get(category, {}).get(plugin_name, {})
        help_text = f"📦 **Plugin:** `{plugin_name.upper()}`\n"
        help_text += "━━━━━━━━━━━━━━━━━━━━\n"
        if commands:
            for cmd, info in commands.items():
                help_text += f"• `.{cmd}` : {info}\n"
        else:
            help_text += "_Tidak ada informasi perintah._"
        
        await callback_query.edit_message_text(
            help_text, 
            reply_markup=await get_plugin_detail_markup(userbot, category, plugin_name, back_page)
        )

    # 4. Logika Toggle (Control Center)
    elif data.startswith("utog_"):
        await callback_query.answer("⚡ Diupdate...")
        _, key, category, plugin_name, back_page = data.split("_")
        
        if key == "lang_switch":
            curr = await userbot.db.get("lang", "id")
            await userbot.db.set("lang", "en" if curr == "id" else "id")
        else:
            curr = await userbot.db.get(key, False)
            await userbot.db.set(key, not curr)
        
        # Refresh halaman detail
        await callback_query.edit_message_reply_markup(
            reply_markup=await get_plugin_detail_markup(userbot, category, plugin_name, back_page)
        )

    # 5. Kontrol Lainnya
    elif data == "close_db":
        await callback_query.answer("🗑 Menutup...")
        await callback_query.message.delete()
    
    elif data == "page_info":
        await callback_query.answer("Gunakan tombol panah untuk berpindah halaman.", show_alert=True)
    
    elif data == "afk_status_info":
        await callback_query.answer("Status AFK hanya bisa diaktifkan/matikan via perintah .afk", show_alert=True)

# --- CONTACT HANDLER (Menjaga Integrasi main.py) ---
async def assistant_contact_handler(client, message: Message):
    me = client.parent.me
    if message.from_user.id == me.id: return
    log_text = f"📩 **Pesan Baru di Assistant Bot**\n\n**Dari:** {message.from_user.mention} (`{message.from_user.id}`)\n**Pesan:** {message.text or '[Media]'}"
    try:
        await client.parent.send_message("me", log_text)
        await message.reply("✅ Pesan kamu telah diteruskan ke Bos saya.")
    except: pass
