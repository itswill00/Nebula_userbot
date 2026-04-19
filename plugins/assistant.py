import os
from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from core.decorators import on_cmd, CMD_HELP

# --- CONFIGURATION ---
PLUGINS_PER_PAGE = 12  # Jumlah plugin per halaman (Grid 4x3 atau 3x4)

# --- PAGINATION ENGINE ---

def get_all_plugins():
    """Mengambil daftar semua plugin unik secara flat (tanpa kategori)."""
    all_plugins = []
    for cat in CMD_HELP:
        for plug in CMD_HELP[cat]:
            if plug not in all_plugins:
                all_plugins.append((plug, cat))
    return sorted(all_plugins)

async def get_help_markup(page=0):
    """Menghasilkan Markup Grid dengan Navigasi Halaman (Prev/Next)."""
    plugins = get_all_plugins()
    count = len(plugins)
    
    # Hitung total halaman
    total_pages = (count - 1) // PLUGINS_PER_PAGE
    if page < 0: page = total_pages
    if page > total_pages: page = 0
    
    # Ambil plugin untuk halaman ini
    start = page * PLUGINS_PER_PAGE
    stop = start + PLUGINS_PER_PAGE
    page_plugins = plugins[start:stop]
    
    buttons = []
    # Buat Grid 3 Kolom
    for row in [page_plugins[i:i+3] for i in range(0, len(page_plugins), 3)]:
        buttons.append([
            InlineKeyboardButton(p[0].title(), callback_data=f"hplug_{p[1]}_{p[0]}_{page}") for p in row
        ])
    
    # Tombol Navigasi (Prev | Page/Total | Next)
    nav_buttons = []
    nav_buttons.append(InlineKeyboardButton("«", callback_data=f"hpage_{page-1}"))
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages+1}", callback_data="hpage_info"))
    nav_buttons.append(InlineKeyboardButton("»", callback_data=f"hpage_{page+1}"))
    
    buttons.append(nav_buttons)
    buttons.append([InlineKeyboardButton("🗑 Tutup", callback_data="close_db")])
    
    return InlineKeyboardMarkup(buttons)

# --- CALLBACK HANDLERS ---

async def assistant_callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    me = client.parent.me
    
    if callback_query.from_user.id != me.id:
        return await callback_query.answer("🚫 Akses Ditolak.", show_alert=True)

    # 1. Navigasi Halaman (Next/Prev)
    if data.startswith("hpage_"):
        if data == "hpage_info":
            return await callback_query.answer(f"Total Plugin: {len(get_all_plugins())}", show_alert=True)
            
        page = int(data.split("_")[1])
        await callback_query.answer()
        await callback_query.edit_message_reply_markup(reply_markup=await get_help_markup(page))

    # 2. Detail Plugin
    elif data.startswith("hplug_"):
        await callback_query.answer()
        parts = data.split("_", 3)
        cat, plug, back_page = parts[1], parts[2], parts[3]
        
        commands = CMD_HELP.get(cat, {}).get(plug, {})
        text = f"📦 **Plugin:** `{plug.upper()}`\n━━━━━━━━━━━━━━━━━━━━\n"
        for cmd, info in commands.items():
            text += f"• `.{cmd}` : {info}\n"
        
        buttons = []
        # Logic toggles tetap sama...
        if plug == "antispam":
            is_as = await client.parent.db.get("antispam", False)
            buttons.append([InlineKeyboardButton(f"Anti-Spam: {'✅' if is_as else '❌'}", callback_data=f"htog_antispam_{cat}_{plug}_{back_page}")])
        elif plug == "pmpermit":
            is_pm = await client.parent.db.get("pm_permit_enabled", True)
            buttons.append([InlineKeyboardButton(f"PM-Permit: {'✅' if is_pm else '❌'}", callback_data=f"htog_pm_permit_enabled_{cat}_{plug}_{back_page}")])

        buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data=f"hpage_{back_page}")])
        await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

    # 3. Logika Toggle di dalam halaman Help
    elif data.startswith("htog_"):
        parts = data.split("_", 4)
        key, cat, plug, back_page = parts[1], parts[2], parts[3], parts[4]
        await callback_query.answer("⚡ Diupdate...")
        
        curr = await client.parent.db.get(key, False)
        await client.parent.db.set(key, not curr)
        
        # Refresh halaman detail tersebut
        # Kita panggil ulang logika hplug dengan callback yang sama
        await assistant_callback_handler(client, CallbackQuery(
            id=callback_query.id,
            from_user=callback_query.from_user,
            chat_instance=callback_query.chat_instance,
            message=callback_query.message,
            data=f"hplug_{cat}_{plug}_{back_page}",
            client=client
        ))

    elif data == "close_db":
        await callback_query.answer("🗑 Ditutup.")
        await callback_query.message.delete()

# --- CONTACT BOT LOGIC ---
async def assistant_contact_handler(client, message: Message):
    me = client.parent.me
    if message.from_user.id == me.id: return
    log_text = f"📩 **Pesan Baru di Assistant Bot**\n\n**Dari:** {message.from_user.mention} (`{message.from_user.id}`)\n**Pesan:** {message.text or '[Media]'}"
    try:
        await client.parent.send_message("me", log_text)
        await message.reply("✅ Pesan kamu telah diteruskan ke Bos saya.")
    except: pass
