import os
from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from core.decorators import on_cmd

# --- DATABASE HELPERS ---
async def get_status(client_parent, key, default=False):
    return await client_parent.db.get(key, default)

# --- ULTROID-STYLE UI GENERATOR ---

async def get_dashboard_markup(client_parent):
    """Menghasilkan Grid Menu bergaya Ultroid (2 kolom)."""
    # Ambil status untuk label dinamis
    is_ad = await get_status(client_parent, "anti_delete", True)
    is_as = await get_status(client_parent, "antispam", False)
    is_pm = await get_status(client_parent, "pm_permit_enabled", True)
    
    afk_data = await client_parent.db.get("afk", {"is_afk": False})
    is_afk = afk_data.get("is_afk", False)
    
    lang = await get_status(client_parent, "lang", "id")

    # Grid 2 Kolom
    buttons = [
        [
            InlineKeyboardButton(f"{'✅' if is_ad else '❌'} Anti-Delete", callback_data="set_anti_delete"),
            InlineKeyboardButton(f"{'✅' if is_as else '❌'} Anti-Spam", callback_data="set_antispam")
        ],
        [
            InlineKeyboardButton(f"{'✅' if is_pm else '❌'} PM-Permit", callback_data="set_pm_permit_enabled"),
            InlineKeyboardButton(f"{'💤' if is_afk else '⚡'} Status AFK", callback_data="set_afk_info")
        ],
        [
            InlineKeyboardButton(f"🌐 Bahasa: {lang.upper()}", callback_data="set_lang_switch"),
            InlineKeyboardButton("🗑 Tutup", callback_data="close_db")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

# --- COMMANDS ---

@Client.on_message(on_cmd("db", category="Config", info="Dashboard Kontrol Nebula (Ultroid Style)."))
async def open_dashboard(client, message: Message):
    if not client.assistant:
        return await client.fast_edit(message, "✦ Bot Assistant belum aktif.")
    
    text = (
        "🌌 **Nebula Engine Dashboard**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Klik pada tombol di bawah untuk mengelola utilitas Anda secara individu."
    )
    markup = await get_dashboard_markup(client)
    
    try:
        await client.assistant.send_message(message.chat.id, text, reply_markup=markup)
        await message.delete()
    except Exception:
        await client.fast_edit(message, "⚠️ Gagal mengirim Dashboard.")

# --- CALLBACK HANDLERS ---

async def assistant_callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    me = client.parent.me
    
    if callback_query.from_user.id != me.id:
        return await callback_query.answer("🚫 Akses Ditolak.", show_alert=True)

    # Logika Toggle (Set)
    if data.startswith("set_"):
        key = data.replace("set_", "")
        
        if key == "lang_switch":
            current = await client.parent.db.get("lang", "id")
            new_val = "en" if current == "id" else "id"
            await client.parent.db.set("lang", new_val)
            await callback_query.answer(f"🌐 Bahasa diubah ke {new_val.upper()}")
        elif key == "afk_info":
            afk_data = await client.parent.db.get("afk", {"is_afk": False})
            status = "Aktif" if afk_data.get("is_afk") else "Non-Aktif"
            return await callback_query.answer(f"💤 Status AFK: {status}\nGunakan .afk untuk mengubah.", show_alert=True)
        else:
            current = await client.parent.db.get(key, False)
            new_val = not current
            await client.parent.db.set(key, new_val)
            status_str = "DIAKTIFKAN" if new_val else "DIMATIKAN"
            await callback_query.answer(f"✅ {key.replace('_', ' ').title()} {status_str}")

        # Refresh UI
        markup = await get_dashboard_markup(client.parent)
        await callback_query.edit_message_reply_markup(reply_markup=markup)

    elif data == "close_db":
        await callback_query.answer("🗑 Dashboard ditutup.")
        await callback_query.message.delete()

# --- CONTACT BOT LOGIC ---
async def assistant_contact_handler(client, message: Message):
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
