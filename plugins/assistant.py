import os
from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from core.decorators import on_cmd, CMD_HELP

# --- CONFIGURATION ---
PLUGINS_PER_PAGE = 12

# --- PAGINATION ENGINE ---

def get_all_plugins():
    all_plugins = []
    for cat in CMD_HELP:
        for plug in CMD_HELP[cat]:
            if (plug, cat) not in all_plugins:
                all_plugins.append((plug, cat))
    return sorted(all_plugins)

async def get_help_markup(page=0):
    plugins = get_all_plugins()
    count = len(plugins)
    total_pages = (count - 1) // PLUGINS_PER_PAGE
    if page < 0: page = total_pages
    if page > total_pages: page = 0
    
    start = page * PLUGINS_PER_PAGE
    page_plugins = plugins[start : start + PLUGINS_PER_PAGE]
    
    buttons = []
    for row in [page_plugins[i:i+3] for i in range(0, len(page_plugins), 3)]:
        buttons.append([
            InlineKeyboardButton(p[0].title(), callback_data=f"hplug_{p[1]}_{p[0]}_{page}") for p in row
        ])
    
    # Navigasi Bawah
    nav = [
        InlineKeyboardButton("«", callback_data=f"hpage_{page-1}"),
        InlineKeyboardButton(f"{page+1}/{total_pages+1}", callback_data="hpage_info"),
        InlineKeyboardButton("»", callback_data=f"hpage_{page+1}")
    ]
    buttons.append(nav)
    buttons.append([InlineKeyboardButton("🗑 Tutup Menu", callback_data="close_db")])
    return InlineKeyboardMarkup(buttons)

async def get_plugin_page_markup(client_parent, category, plugin_name, back_page):
    """Menampilkan detail plugin + TOMBOL KONTROL (Control Center)."""
    buttons = []
    
    # MAP KONTROL (Mengembalikan Fitur yang Hilang)
    # Menambahkan toggle otomatis jika plugin terdeteksi punya fitur di database
    if plugin_name == "antispam":
        state = await client_parent.db.get("antispam", False)
        buttons.append([InlineKeyboardButton(f"Anti-Spam: {'✅ ON' if state else '❌ OFF'}", callback_data=f"htog_antispam_{category}_{plugin_name}_{back_page}")])
    elif plugin_name == "pmpermit":
        state = await client_parent.db.get("pm_permit_enabled", True)
        buttons.append([InlineKeyboardButton(f"PM Permit: {'✅ ON' if state else '❌ OFF'}", callback_data=f"htog_pm_permit_enabled_{category}_{plugin_name}_{back_page}")])
    elif plugin_name == "assistant" or plugin_name == "anti_delete":
        state = await client_parent.db.get("anti_delete", True)
        buttons.append([InlineKeyboardButton(f"Anti-Delete: {'✅ ON' if state else '❌ OFF'}", callback_data=f"htog_anti_delete_{category}_{plugin_name}_{back_page}")])
    elif plugin_name == "system":
        lang = await client_parent.db.get("lang", "id")
        buttons.append([InlineKeyboardButton(f"Bahasa: {lang.upper()}", callback_data=f"htog_lang_switch_{category}_{plugin_name}_{back_page}")])
    elif plugin_name == "afk":
        afk_data = await client_parent.db.get("afk", {"is_afk": False})
        state = afk_data.get("is_afk")
        buttons.append([InlineKeyboardButton(f"Status: {'AFK 💤' if state else 'ONLINE ⚡'}", callback_data="info_afk")])

    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data=f"hpage_{back_page}")])
    return InlineKeyboardMarkup(buttons)

# --- CALLBACK HANDLERS ---

async def assistant_callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    # Karena ini dijalankan oleh asisten, client.parent adalah Userbot
    userbot = client.parent if hasattr(client, "parent") else client
    me = userbot.me
    
    if callback_query.from_user.id != me.id:
        return await callback_query.answer("🚫 Akses Ditolak.", show_alert=True)

    # 1. Navigasi Halaman (Next/Prev)
    if data.startswith("hpage_"):
        if data == "hpage_info":
            return await callback_query.answer(f"Nebula Engine: {len(get_all_plugins())} Plugins", show_alert=True)
        
        page = int(data.split("_")[1])
        await callback_query.answer()
        text = "🌌 **Nebula Engine - Help Menu**\n━━━━━━━━━━━━━━━━━━━━\nPilih plugin untuk melihat detail dan pengaturan."
        await callback_query.edit_message_text(text, reply_markup=await get_help_markup(page))

    # 2. Halaman Detail Plugin (How-To + Control Center)
    elif data.startswith("hplug_"):
        await callback_query.answer()
        _, cat, plug, page = data.split("_", 3)
        
        commands = CMD_HELP.get(cat, {}).get(plug, {})
        help_text = f"📦 **Plugin:** `{plug.upper()}`\n"
        help_text += "━━━━━━━━━━━━━━━━━━━━\n"
        help_text += "**Perintah Tersedia:**\n"
        for cmd, info in commands.items():
            help_text += f"• `.{cmd}` : {info}\n"
        
        await callback_query.edit_message_text(
            help_text, 
            reply_markup=await get_plugin_page_markup(userbot, cat, plug, page)
        )

    # 3. Logika Kontrol / Toggling (Control Center Logic)
    elif data.startswith("htog_"):
        await callback_query.answer("⚡ Sinkronisasi...")
        _, key, cat, plug, page = data.split("_", 4)
        
        if key == "lang_switch":
            curr = await userbot.db.get("lang", "id")
            await userbot.db.set("lang", "en" if curr == "id" else "id")
        else:
            curr = await userbot.db.get(key, False)
            await userbot.db.set(key, not curr)
        
        # Refresh halaman detail plugin tersebut
        await callback_query.edit_message_reply_markup(
            reply_markup=await get_plugin_page_markup(userbot, cat, plug, page)
        )

    elif data == "close_db":
        await callback_query.answer("🗑 Menutup...")
        await callback_query.message.delete()
    
    elif data == "info_afk":
        await callback_query.answer("Status AFK hanya bisa diubah melalui perintah .afk", show_alert=True)

# --- CONTACT BOT LOGIC ---
async def assistant_contact_handler(client, message: Message):
    me = client.parent.me
    if message.from_user.id == me.id: return
    log_text = f"📩 **Pesan Baru di Assistant Bot**\n\n**Dari:** {message.from_user.mention} (`{message.from_user.id}`)\n**Pesan:** {message.text or '[Media]'}"
    try:
        await client.parent.send_message("me", log_text)
        await message.reply("✅ Pesan kamu telah diteruskan ke Bos saya.")
    except: pass
