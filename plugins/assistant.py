import os
from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from core.decorators import on_cmd

# --- MENU GENERATORS ---

async def get_main_menu_markup():
    """Menu Utama Dashboard."""
    buttons = [
        [
            InlineKeyboardButton("🛡️ Security", callback_data="menu_security"),
            InlineKeyboardButton("👤 Identity", callback_data="menu_identity")
        ],
        [
            InlineKeyboardButton("🛠️ Tools", callback_data="menu_tools"),
            InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")
        ],
        [
            InlineKeyboardButton("🗑 Tutup Dashboard", callback_data="close_db")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

async def get_security_menu_markup(client_parent):
    """Sub-menu Keamanan."""
    is_ad = await client_parent.db.get("anti_delete", True)
    is_as = await client_parent.db.get("antispam", False)
    is_pm = await client_parent.db.get("pm_permit_enabled", True)
    
    buttons = [
        [InlineKeyboardButton(f"Anti-Delete: {'✅' if is_ad else '❌'}", callback_data="conf_anti_delete")],
        [InlineKeyboardButton(f"Anti-Spam: {'✅' if is_as else '❌'}", callback_data="conf_antispam")],
        [InlineKeyboardButton(f"PM Permit: {'✅' if is_pm else '❌'}", callback_data="conf_pm_permit_enabled")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(buttons)

async def get_identity_menu_markup(client_parent):
    """Sub-menu Identitas."""
    afk_data = await client_parent.db.get("afk", {"is_afk": False})
    is_afk = afk_data.get("is_afk", False)
    
    buttons = [
        [InlineKeyboardButton(f"Status AFK: {'Aktif 💤' if is_afk else 'Online ⚡'}", callback_data="info_afk")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(buttons)

async def get_settings_menu_markup(client_parent):
    """Sub-menu Pengaturan Umum."""
    lang = await client_parent.db.get("lang", "id")
    
    buttons = [
        [InlineKeyboardButton(f"Bahasa: {lang.upper()}", callback_data="conf_lang_switch")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(buttons)

# --- COMMANDS ---

@Client.on_message(on_cmd("db", category="Config", info="Pusat kontrol pengaturan fitur Nebula."))
async def open_dashboard(client, message: Message):
    if not client.assistant:
        return await client.fast_edit(message, "✦ Bot Assistant kamu belum aktif nih.")
    
    text = "🛠 **Nebula Engine Dashboard**\n\nSilakan pilih kategori pengaturan yang ingin Anda kelola:"
    markup = await get_main_menu_markup()
    
    try:
        await client.assistant.send_message(message.chat.id, text, reply_markup=markup)
        await message.delete()
    except Exception:
        await client.fast_edit(message, f"{text}\n\n⚠️ Gagal membuka dashboard via Assistant.")

# --- CALLBACK HANDLERS ---

async def assistant_callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    me = client.parent.me
    
    if callback_query.from_user.id != me.id:
        return await callback_query.answer("🚫 Akses Ditolak.", show_alert=True)

    # 1. Navigasi Menu
    if data == "menu_main":
        await callback_query.answer()
        text = "🛠 **Nebula Engine Dashboard**\n\nSilakan pilih kategori pengaturan yang ingin Anda kelola:"
        await callback_query.edit_message_text(text, reply_markup=await get_main_menu_markup())

    elif data == "menu_security":
        await callback_query.answer()
        text = "🛡 **Security Settings**\nKelola proteksi dan keamanan akun Anda."
        await callback_query.edit_message_text(text, reply_markup=await get_security_menu_markup(client.parent))

    elif data == "menu_identity":
        await callback_query.answer()
        text = "👤 **Identity Settings**\nKelola profil dan status keberadaan Anda."
        await callback_query.edit_message_text(text, reply_markup=await get_identity_menu_markup(client.parent))

    elif data == "menu_settings":
        await callback_query.answer()
        text = "⚙️ **General Settings**\nAtur preferensi bahasa dan sistem bot."
        await callback_query.edit_message_text(text, reply_markup=await get_settings_menu_markup(client.parent))

    # 2. Logika Konfigurasi (Toggle)
    elif data.startswith("conf_"):
        await callback_query.answer("⚡ Mengupdate...")
        key = data.replace("conf_", "")
        
        if key == "lang_switch":
            current = await client.parent.db.get("lang", "id")
            new_val = "en" if current == "id" else "id"
            await client.parent.db.set("lang", new_val)
            await callback_query.edit_message_reply_markup(reply_markup=await get_settings_menu_markup(client.parent))
        else:
            current = await client.parent.db.get(key, False)
            await client.parent.db.set(key, not current)
            await callback_query.edit_message_reply_markup(reply_markup=await get_security_menu_markup(client.parent))

    # 3. Logika Penutupan
    elif data == "close_db":
        await callback_query.answer("🗑 Menutup Dashboard.")
        await callback_query.message.delete()
    
    elif data == "info_afk":
        await callback_query.answer("Gunakan perintah .afk untuk mengubah status.", show_alert=True)

# --- CONTACT BOT LOGIC ---
async def assistant_contact_handler(client, message: Message):
    """Menangani pesan dari orang asing ke Assistant Bot."""
    me = client.parent.me
    if message.from_user.id == me.id:
        return

    log_text = (
        f"📩 **Pesan Baru di Assistant Bot**\n\n"
        f"**Dari:** {message.from_user.mention} (`{message.from_user.id}`)\n"
        f"**Pesan:** {message.text or '[Media]'}"
    )
    
    try:
        await client.parent.send_message("me", log_text)
        await message.reply("✅ Pesan kamu telah diteruskan ke Bos saya.")
    except Exception:
        pass
