import os
import math
from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from core.decorators import on_cmd, CMD_HELP

# --- HELPERS ---

def chunk_list(lst, n):
    """Membagi list menjadi bagian-bagian kecil (untuk grid)."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# --- MODULAR UI GENERATORS (ULTROID STYLE) ---

async def get_modules_grid_markup():
    """Menampilkan daftar NAMA MODUL dalam grid 3 kolom (Halaman Utama)."""
    modules = sorted(CMD_HELP.keys())
    buttons = []
    
    # Buat grid 3 kolom berisi nama-nama kategori/modul
    for row in chunk_list(modules, 3):
        buttons.append([
            InlineKeyboardButton(mod, callback_data=f"modul_{mod}") for mod in row
        ])
    
    buttons.append([InlineKeyboardButton("🗑 Tutup", callback_data="close_db")])
    return InlineKeyboardMarkup(buttons)

async def get_module_detail_markup(client_parent, category):
    """Menampilkan detail utilitas & tombol kontrol untuk modul tertentu."""
    buttons = []
    
    # 1. Tambahkan tombol toggle spesifik berdasarkan kategori
    if category == "Security":
        is_ad = await client_parent.db.get("anti_delete", True)
        is_as = await client_parent.db.get("antispam", False)
        is_pm = await client_parent.db.get("pm_permit_enabled", True)
        
        buttons.append([InlineKeyboardButton(f"Anti-Delete: {'✅' if is_ad else '❌'}", callback_data="toggle_anti_delete")])
        buttons.append([InlineKeyboardButton(f"Anti-Spam: {'✅' if is_as else '❌'}", callback_data="toggle_antispam")])
        buttons.append([InlineKeyboardButton(f"PM-Permit: {'✅' if is_pm else '❌'}", callback_data="toggle_pm_permit_enabled")])
    
    elif category == "Identity":
        afk_data = await client_parent.db.get("afk", {"is_afk": False})
        is_afk = afk_data.get("is_afk", False)
        buttons.append([InlineKeyboardButton(f"Status AFK: {'Aktif 💤' if is_afk else 'Online ⚡'}", callback_data="info_afk")])

    elif category == "System":
        lang = await client_parent.db.get("lang", "id")
        buttons.append([InlineKeyboardButton(f"Bahasa: {lang.upper()}", callback_data="toggle_lang_switch")])

    # 2. Tombol Navigasi
    buttons.append([InlineKeyboardButton("⬅️ Kembali", callback_data="back_to_modules")])
    
    return InlineKeyboardMarkup(buttons)

# --- COMMANDS ---

@Client.on_message(on_cmd("db", category="Config", info="Pusat Modul Nebula (Gaya Ultroid)."))
async def open_dashboard(client, message: Message):
    if not client.assistant:
        return await client.fast_edit(message, "✦ Bot Assistant belum aktif.")
    
    text = (
        "✨ **Nebula Engine - Modules**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"Ditemukan **{len(CMD_HELP)}** modul terpasang.\n"
        "Pilih modul untuk melihat detail dan pengaturan."
    )
    markup = await get_modules_grid_markup()
    
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

    # A. NAVIGASI MODUL
    if data == "back_to_modules":
        await callback_query.answer()
        text = "✨ **Nebula Engine - Modules**\n━━━━━━━━━━━━━━━━━━━━\nPilih modul untuk melihat detail."
        await callback_query.edit_message_text(text, reply_markup=await get_modules_grid_markup())

    elif data.startswith("modul_"):
        await callback_query.answer()
        category = data.replace("modul_", "")
        
        # Buat teks bantuan ala Ultroid
        help_info = f"📦 **Modul:** `{category}`\n"
        help_info += "━━━━━━━━━━━━━━━━━━━━\n"
        if category in CMD_HELP:
            for cmd, info in CMD_HELP[category].items():
                help_info += f"• `.{cmd}` : {info}\n"
        
        await callback_query.edit_message_text(
            help_info, 
            reply_markup=await get_module_detail_markup(client.parent, category)
        )

    # B. LOGIKA TOGGLE (Di dalam Modul)
    elif data.startswith("toggle_"):
        key = data.replace("toggle_", "")
        await callback_query.answer("⚡ Diupdate...")
        
        if key == "lang_switch":
            current = await client.parent.db.get("lang", "id")
            await client.parent.db.set("lang", "en" if current == "id" else "id")
            await callback_query.edit_message_reply_markup(reply_markup=await get_module_detail_markup(client.parent, "System"))
        else:
            current = await client.parent.db.get(key, False)
            await client.parent.db.set(key, not current)
            await callback_query.edit_message_reply_markup(reply_markup=await get_module_detail_markup(client.parent, "Security"))

    # C. LAIN-LAIN
    elif data == "close_db":
        await callback_query.answer("🗑 Ditutup.")
        await callback_query.message.delete()
    
    elif data == "info_afk":
        await callback_query.answer("Status AFK hanya bisa diubah via perintah .afk", show_alert=True)

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
