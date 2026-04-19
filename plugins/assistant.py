import os
from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from core.decorators import on_cmd

# --- DASHBOARD UI GENERATOR ---

async def get_dashboard_markup(client_parent):
    """Fungsi pembantu untuk membuat markup dashboard terbaru."""
    is_ad = await client_parent.db.get("anti_delete", True)
    is_as = await client_parent.db.get("antispam", False)
    lang = await client_parent.db.get("lang", "id")
    
    buttons = [
        [
            InlineKeyboardButton(f"Anti-Delete: {'✅' if is_ad else '❌'}", callback_data="conf_anti_delete"),
            InlineKeyboardButton(f"Anti-Spam: {'✅' if is_as else '❌'}", callback_data="conf_antispam")
        ],
        [
            InlineKeyboardButton(f"Bahasa: {lang.upper()}", callback_data="conf_lang_switch")
        ],
        [
            InlineKeyboardButton("🗑 Tutup Dashboard", callback_data="close_db")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

# --- COMMANDS ---

@Client.on_message(on_cmd("db", category="Config", info="Pusat kontrol pengaturan fitur Nebula."))
async def open_dashboard(client, message: Message):
    """Membuka Dashboard Kontrol melalui Assistant Bot."""
    if not client.assistant:
        return await client.fast_edit(message, "✦ Bot Assistant kamu belum aktif nih.")
    
    text = f"🛠 **Nebula Engine Dashboard**\n\nSelamat datang di pusat kendali Nebula. Gunakan tombol di bawah untuk mengatur fitur bot kamu."
    reply_markup = await get_dashboard_markup(client)
    
    try:
        await client.assistant.send_message(
            message.chat.id, 
            text, 
            reply_markup=reply_markup
        )
        await message.delete()
    except Exception:
        await client.fast_edit(message, f"{text}\n\n⚠️ **Catatan:** Coba `/start` di bot asisten kamu.")

# --- CALLBACK HANDLERS ---

async def assistant_callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    me = client.parent.me
    
    # Keamanan: Hanya pemilik yang bisa klik
    if callback_query.from_user.id != me.id:
        return await callback_query.answer("🚫 Akses Ditolak.", show_alert=True)

    # 1. Handling Konfigurasi (Toggle ON/OFF)
    if data.startswith("conf_"):
        key = data.replace("conf_", "")
        
        if key == "lang_switch":
            current = await client.parent.db.get("lang", "id")
            new_val = "en" if current == "id" else "id"
            await client.parent.db.set("lang", new_val)
        else:
            current = await client.parent.db.get(key, (True if key == "anti_delete" else False))
            new_val = not current
            await client.parent.db.set(key, new_val)
        
        # Berikan feedback instan agar tidak hang
        await callback_query.answer("✨ Perubahan Disimpan!")
        
        # Update tampilan UI
        text = f"🛠 **Nebula Engine Dashboard**\n\nSelamat datang di pusat kendali Nebula. Gunakan tombol di bawah untuk mengatur fitur bot kamu."
        markup = await get_dashboard_markup(client.parent)
        await callback_query.edit_message_text(text, reply_markup=markup)

    # 2. Handling Tutup Dashboard
    elif data == "close_db":
        await callback_query.answer("Menutup...")
        try:
            if callback_query.message:
                await callback_query.message.delete()
            elif callback_query.inline_message_id:
                # Untuk pesan inline (jarang terjadi di DB tapi antisipasi)
                await client.edit_message_text(inline_message_id=callback_query.inline_message_id, text="🗑 Dashboard ditutup.")
        except Exception:
            pass

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
