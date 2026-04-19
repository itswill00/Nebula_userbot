import os
from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from core.decorators import on_cmd

# --- FULL DASHBOARD GENERATOR ---

async def get_full_dashboard_markup(client_parent):
    """Membuat dashboard dengan semua tombol utilitas sekaligus (Flat Layout)."""
    # Ambil semua status dari cache memori database
    is_ad = await client_parent.db.get("anti_delete", True)
    is_as = await client_parent.db.get("antispam", False)
    is_pm = await client_parent.db.get("pm_permit_enabled", True)
    lang = await client_parent.db.get("lang", "id")
    afk_data = await client_parent.db.get("afk", {"is_afk": False})
    is_afk = afk_data.get("is_afk", False)

    buttons = [
        # Baris 1: Keamanan Utama
        [
            InlineKeyboardButton(f"🛡️ Anti-Delete: {'✅' if is_ad else '❌'}", callback_data="conf_anti_delete"),
        ],
        [
            InlineKeyboardButton(f"🚫 Anti-Spam: {'✅' if is_as else '❌'}", callback_data="conf_antispam"),
        ],
        # Baris 2: Privasi
        [
            InlineKeyboardButton(f"🔑 PM Permit: {'✅' if is_pm else '❌'}", callback_data="conf_pm_permit_enabled"),
        ],
        # Baris 3: Status & Bahasa
        [
            InlineKeyboardButton(f"💤 Status: {'AFK' if is_afk else 'ONLINE'}", callback_data="info_afk"),
            InlineKeyboardButton(f"🌐 Bahasa: {lang.upper()}", callback_data="conf_lang_switch")
        ],
        # Baris Akhir: Kontrol
        [
            InlineKeyboardButton("🗑 Tutup Dashboard", callback_data="close_db")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

# --- COMMANDS ---

@Client.on_message(on_cmd("db", category="Config", info="Pusat kontrol pengaturan fitur Nebula."))
async def open_dashboard(client, message: Message):
    if not client.assistant:
        return await client.fast_edit(message, "✦ Bot Assistant kamu belum aktif nih.")
    
    text = "🛠 **Nebula Engine Dashboard**\n\nSemua utilitas Anda tersedia di bawah ini. Klik tombol untuk mengaktifkan atau menonaktifkan fitur secara instan."
    markup = await get_full_dashboard_markup(client)
    
    try:
        await client.assistant.send_message(message.chat.id, text, reply_markup=markup)
        await message.delete()
    except Exception:
        await client.fast_edit(message, f"{text}\n\n⚠️ Gagal membuka dashboard via Assistant.")

# --- CALLBACK HANDLERS ---

async def assistant_callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    me = client.parent.me
    
    # Keamanan: Hanya pemilik yang bisa klik
    if callback_query.from_user.id != me.id:
        return await callback_query.answer("🚫 Akses Ditolak.", show_alert=True)

    # 1. Logika Konfigurasi (Toggle Langsung)
    if data.startswith("conf_"):
        key = data.replace("conf_", "")
        
        # Kirim answer dulu agar tidak hang
        await callback_query.answer("⚡ Memproses...")
        
        if key == "lang_switch":
            current = await client.parent.db.get("lang", "id")
            new_val = "en" if current == "id" else "id"
            await client.parent.db.set("lang", new_val)
        else:
            current = await client.parent.db.get(key, False)
            await client.parent.db.set(key, not current)
        
        # Update tampilan UI secara instan (Flat Update)
        markup = await get_full_dashboard_markup(client.parent)
        await callback_query.edit_message_reply_markup(reply_markup=markup)

    # 2. Logika Penutupan
    elif data == "close_db":
        await callback_query.answer("🗑 Dashboard ditutup.")
        await callback_query.message.delete()
    
    # 3. Info Buttons
    elif data == "info_afk":
        afk_data = await client.parent.db.get("afk", {"is_afk": False})
        status = "Sedang AFK" if afk_data.get("is_afk") else "Sedang Online"
        await callback_query.answer(f"ℹ️ Status saat ini: {status}\nGunakan perintah .afk untuk mengubah.", show_alert=True)

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
