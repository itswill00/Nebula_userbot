import os
from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from core.decorators import on_cmd, CMD_HELP

# --- HELPERS ---
def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# --- MODULAR UI GENERATORS ---

async def get_main_menu_markup():
    """Halaman Utama: Daftar Kategori."""
    # Ambil semua kategori unik dari CMD_HELP
    categories = sorted(CMD_HELP.keys())
    buttons = []
    for row in chunk_list(categories, 2):
        buttons.append([
            InlineKeyboardButton(f"📁 {cat}", callback_data=f"cat_{cat}") for cat in row
        ])
    buttons.append([InlineKeyboardButton("🗑 Tutup Dashboard", callback_data="close_db")])
    return InlineKeyboardMarkup(buttons)

async def get_plugin_list_markup(category):
    """Halaman Kategori: Daftar Plugin sebagai tombol individu."""
    if category not in CMD_HELP:
        return None
    
    plugins = sorted(CMD_HELP[category].keys())
    buttons = []
    
    # Setiap plugin jadi satu tombol sendiri
    for row in chunk_list(plugins, 2):
        buttons.append([
            InlineKeyboardButton(f"📦 {p.title()}", callback_data=f"plug_{category}_{p}") for p in row
        ])
    
    buttons.append([InlineKeyboardButton("⬅️ Kembali ke Menu", callback_data="back_to_main")])
    return InlineKeyboardMarkup(buttons)

async def get_plugin_detail_markup(client_parent, category, plugin_name):
    """Halaman Plugin: Detail penggunaan & tombol kontrol spesifik plugin tersebut."""
    buttons = []
    
    # Tombol Kontrol Spesifik per Plugin
    if plugin_name == "antispam":
        is_as = await client_parent.db.get("antispam", False)
        buttons.append([InlineKeyboardButton(f"Anti-Spam: {'✅' if is_as else '❌'}", callback_data="toggle_antispam")])
    
    elif plugin_name == "pmpermit":
        is_pm = await client_parent.db.get("pm_permit_enabled", True)
        buttons.append([InlineKeyboardButton(f"PM-Permit: {'✅' if is_pm else '❌'}", callback_data="toggle_pm_permit_enabled")])
    
    elif plugin_name == "afk":
        afk_data = await client_parent.db.get("afk", {"is_afk": False})
        buttons.append([InlineKeyboardButton(f"Status AFK: {'Aktif 💤' if afk_data.get('is_afk') else 'Online ⚡'}", callback_data="info_afk")])

    elif plugin_name == "system":
        lang = await client_parent.db.get("lang", "id")
        buttons.append([InlineKeyboardButton(f"Bahasa: {lang.upper()}", callback_data="toggle_lang_switch")])
        
    elif plugin_name == "tools":
        # Contoh tombol tambahan untuk plugin tools
        buttons.append([InlineKeyboardButton("☁️ Weather Settings", callback_data="info_tools")])

    # Tombol Kembali ke daftar plugin di kategori yang sama
    buttons.append([InlineKeyboardButton(f"⬅️ Kembali ke {category}", callback_data=f"cat_{category}")])
    
    return InlineKeyboardMarkup(buttons)

# --- COMMANDS ---

@Client.on_message(on_cmd("db", category="Config", info="Pusat Kendali Modular Nebula."))
async def open_dashboard(client, message: Message):
    if not client.assistant:
        return await client.fast_edit(message, "✦ Bot Assistant tidak aktif.")
    
    text = "🛠 **Nebula Engine - Dashboard**\nPilih kategori untuk mengelola fitur bot Anda:"
    markup = await get_main_menu_markup()
    try:
        await client.assistant.send_message(message.chat.id, text, reply_markup=markup)
        await message.delete()
    except Exception:
        await client.fast_edit(message, "⚠️ Gagal membuka dashboard.")

# --- CALLBACK HANDLERS ---

async def assistant_callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    me = client.parent.me
    
    if callback_query.from_user.id != me.id:
        return await callback_query.answer("🚫 Akses Ditolak.", show_alert=True)

    # 1. Navigasi ke Menu Utama
    if data == "back_to_main":
        await callback_query.answer()
        await callback_query.edit_message_text(
            "🛠 **Nebula Engine - Dashboard**\nPilih kategori untuk mengelola fitur bot Anda:",
            reply_markup=await get_main_menu_markup()
        )

    # 2. Navigasi ke Daftar Plugin (Modul)
    elif data.startswith("cat_"):
        await callback_query.answer()
        category = data.replace("cat_", "")
        text = f"📂 **Kategori:** `{category}`\nPilih plugin di bawah untuk melihat cara pakai & pengaturan:"
        await callback_query.edit_message_text(text, reply_markup=await get_plugin_list_markup(category))

    # 3. Navigasi ke Detail Plugin Tertentu
    elif data.startswith("plug_"):
        await callback_query.answer()
        parts = data.split("_", 2)
        category, plugin_name = parts[1], parts[2]
        
        # Ambil info perintah dari CMD_HELP
        commands_info = CMD_HELP.get(category, {}).get(plugin_name, {})
        help_text = f"📦 **Plugin:** `{plugin_name.upper()}`\n"
        help_text += f"📂 **Kategori:** `{category}`\n"
        help_text += "━━━━━━━━━━━━━━━━━━━━\n"
        help_text += "**Cara Penggunaan:**\n"
        for cmd, info in commands_info.items():
            help_text += f"• `.{cmd}` : {info}\n"
        
        await callback_query.edit_message_text(
            help_text, 
            reply_markup=await get_plugin_detail_markup(client.parent, category, plugin_name)
        )

    # 4. Logika Toggle (On/Off)
    elif data.startswith("toggle_"):
        key = data.replace("toggle_", "")
        await callback_query.answer("⚡ Diupdate...")
        
        # Update Database
        if key == "lang_switch":
            curr = await client.parent.db.get("lang", "id")
            await client.parent.db.set("lang", "en" if curr == "id" else "id")
            # Refresh UI (Asumsi System/system)
            await callback_query.edit_message_reply_markup(reply_markup=await get_plugin_detail_markup(client.parent, "System", "system"))
        else:
            curr = await client.parent.db.get(key, False)
            await client.parent.db.set(key, not curr)
            # Refresh UI (Deteksi otomatis plugin dari key)
            p_name = "pmpermit" if "pm" in key else ("antispam" if "spam" in key else "assistant")
            await callback_query.edit_message_reply_markup(reply_markup=await get_plugin_detail_markup(client.parent, "Security", p_name))

    # 5. Kontrol Dasar
    elif data == "close_db":
        await callback_query.answer("🗑 Dashboard ditutup.")
        await callback_query.message.delete()
    
    elif data.startswith("info_"):
        await callback_query.answer("Info: Gunakan perintah teks untuk pengaturan lebih lanjut.", show_alert=True)

# --- CONTACT BOT LOGIC ---
async def assistant_contact_handler(client, message: Message):
    me = client.parent.me
    if message.from_user.id == me.id: return
    log_text = f"📩 **Pesan Baru di Assistant Bot**\n\n**Dari:** {message.from_user.mention} (`{message.from_user.id}`)\n**Pesan:** {message.text or '[Media]'}"
    try:
        await client.parent.send_message("me", log_text)
        await message.reply("✅ Pesan kamu telah diteruskan ke Bos saya.")
    except: pass
