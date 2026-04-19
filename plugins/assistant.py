import os
from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from core.decorators import on_cmd

# --- DASHBOARD & CALLBACK HANDLER ---

@Client.on_message(on_cmd("db", category="Config", info="Pusat kontrol pengaturan fitur Nebula."))
async def open_dashboard(client, message: Message):
    """Membuka Dashboard Kontrol melalui Assistant Bot."""
    if not client.assistant:
        return await client.fast_edit(message, "✦ Bot Assistant kamu belum aktif nih.")
    
    # Ambil status saat ini
    is_ad = await client.db.get("anti_delete", True)
    is_as = await client.db.get("antispam", False)
    lang = await client.db.get("lang", "id")

    text = f"🛠 **Nebula Engine Dashboard**\n\nSelamat datang di pusat kendali Nebula. Gunakan tombol di bawah untuk mengatur fitur bot kamu."
    
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
    
    try:
        # Kirim pesan via Assistant
        await client.assistant.send_message(
            message.chat.id, 
            text, 
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await message.delete()
    except Exception:
        # Fallback jika Bot tidak ada di chat atau gagal delete
        await client.fast_edit(message, f"{text}\n\n⚠️ **Catatan:** Coba `/start` dulu di bot asisten kamu atau pastikan dia admin di grup ini.")

# Handler untuk Assistant Bot (CallbackQuery)
async def assistant_callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    # OPTIMASI: Gunakan client.parent.me (cached) daripada await get_me()
    me = client.parent.me
    
    if callback_query.from_user.id != me.id:
        return await callback_query.answer("🚫 Akses Ditolak: Hanya pemilik akun yang bisa mengontrol.", show_alert=True)

    if data.startswith("conf_"):
        key = data.replace("conf_", "")
        
        # Logika switch bahasa atau boolean
        if key == "lang_switch":
            current = await client.parent.db.get("lang", "id")
            new_val = "en" if current == "id" else "id"
            await client.parent.db.set("lang", new_val)
        else:
            current = await client.parent.db.get(key, (True if key == "anti_delete" else False))
            new_val = not current
            await client.parent.db.set(key, new_val)
        
        # Refresh Dashboard dengan data terbaru
        is_ad = await client.parent.db.get("anti_delete", True)
        is_as = await client.parent.db.get("antispam", False)
        lang = await client.parent.db.get("lang", "id")
        
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
        
        text = f"🛠 **Nebula Engine Dashboard**\n\nSelamat datang di pusat kendali Nebula. Gunakan tombol di bawah untuk mengatur fitur bot kamu."
        
        try:
            await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
            await callback_query.answer("✨ Pengaturan diperbarui!")
        except Exception:
            await callback_query.answer("⚠️ Gagal memperbarui tampilan.")

    elif data == "close_db":
        # PERBAIKAN: Gunakan delete_messages() yang lebih aman jika message is None
        try:
            if callback_query.message:
                await callback_query.message.delete()
            else:
                await client.delete_messages(callback_query.message.chat.id, callback_query.message.id)
        except Exception:
            await callback_query.answer("Pesan sudah dihapus atau tidak ditemukan.")

# --- CONTACT BOT LOGIC ---
async def assistant_contact_handler(client, message: Message):
    me = client.parent.me
    if message.from_user.id == me.id:
        return

    # Kirim notifikasi ke Saved Messages (me)
    log_text = (
        f"📩 **Pesan Baru di Assistant Bot**\n\n"
        f"**Dari:** {message.from_user.mention} (`{message.from_user.id}`)\n"
        f"**Pesan:** {message.text or '[Media]'}"
    )
    
    try:
        await client.parent.send_message("me", log_text)
        await message.reply("✅ Pesan kamu telah diteruskan ke Bos saya. Silakan tunggu balasan beliau.")
    except Exception:
        pass
