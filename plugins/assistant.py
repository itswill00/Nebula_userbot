import os
import math
from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from core.decorators import on_cmd, CMD_HELP

# --- HELPERS ---
def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# --- UI GENERATORS (THE REAL ULTROID STYLE) ---

async def get_main_help_menu():
    """Halaman 0: Menu Utama Kategori (Official, Addons, Settings)."""
    buttons = [
        [
            InlineKeyboardButton("📦 Official Plugins", callback_data="cat_Identity"),
            InlineKeyboardButton("🛡️ Security Center", callback_data="cat_Security")
        ],
        [
            InlineKeyboardButton("🛠️ System Tools", callback_data="cat_System"),
            InlineKeyboardButton("⚙️ General Settings", callback_data="cat_Config")
        ],
        [
            InlineKeyboardButton("🗑 Tutup Menu", callback_data="close_db")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

async def get_plugin_list_markup(category):
    """Halaman 1: Daftar Nama File Plugin (Grid 3 Kolom) dalam Kategori."""
    if category not in CMD_HELP:
        return None
    
    plugins = sorted(CMD_HELP[category].keys())
    buttons = []
    
    # Grid 3 Kolom berisi nama-nama file plugin (misal: afk, antispam)
    for row in chunk_list(plugins, 3):
        buttons.append([
            InlineKeyboardButton(f"• {p} •", callback_data=f"plug_{category}_{p}") for p in row
        ])
    
    buttons.append([InlineKeyboardButton("⬅️ Kembali ke Menu", callback_data="back_to_main")])
    return InlineKeyboardMarkup(buttons)

async def get_plugin_detail_markup(client_parent, category, plugin_name):
    """Halaman 2: Detail Perintah di dalam Plugin & Tombol Khusus (Jika Ada)."""
    buttons = []
    
    # 1. Tambahkan tombol toggle jika plugin ini punya fungsi khusus (Identity, Security, System)
    if category == "Security":
        if plugin_name == "antispam":
            is_as = await client_parent.db.get("antispam", False)
            buttons.append([InlineKeyboardButton(f"Anti-Spam: {'✅' if is_as else '❌'}", callback_data="toggle_antispam")])
        elif plugin_name == "pmpermit":
            is_pm = await client_parent.db.get("pm_permit_enabled", True)
            buttons.append([InlineKeyboardButton(f"PM-Permit: {'✅' if is_pm else '❌'}", callback_data="toggle_pm_permit_enabled")])
        elif plugin_name == "anti_delete" or plugin_name == "assistant": # Asumsi toggle anti_delete
            is_ad = await client_parent.db.get("anti_delete", True)
            buttons.append([InlineKeyboardButton(f"Anti-Delete: {'✅' if is_ad else '❌'}", callback_data="toggle_anti_delete")])
    
    elif category == "Identity" and plugin_name == "afk":
        afk_data = await client_parent.db.get("afk", {"is_afk": False})
        buttons.append([InlineKeyboardButton(f"Status AFK: {'Aktif 💤' if afk_data.get('is_afk') else 'Online ⚡'}", callback_data="info_afk")])

    elif category == "System" and plugin_name == "system":
        lang = await client_parent.db.get("lang", "id")
        buttons.append([InlineKeyboardButton(f"Bahasa: {lang.upper()}", callback_data="toggle_lang_switch")])

    # 2. Navigasi Kembali ke daftar plugin dalam kategori tersebut
    buttons.append([InlineKeyboardButton("⬅️ Kembali ke Daftar", callback_data=f"cat_{category}")])
    
    return InlineKeyboardMarkup(buttons)

# --- COMMANDS ---

@Client.on_message(on_cmd("db", category="Config", info="Nebula Modular Dashboard (Ultroid Style)."))
async def open_dashboard(client, message: Message):
    if not client.assistant:
        return await client.fast_edit(message, "✦ Bot Assistant belum aktif.")
    
    text = (
        "🌌 **Nebula Engine Dashboard**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Pilih kategori modul di bawah ini untuk mengelola asisten Anda."
    )
    markup = await get_main_help_menu()
    
    try:
        await client.assistant.send_message(message.chat.id, text, reply_markup=markup)
        await message.delete()
    except Exception:
        await client.fast_edit(message, "⚠️ Gagal mengirim Dashboard via Assistant.")

# --- CALLBACK HANDLERS ---

async def assistant_callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    me = client.parent.me
    
    if callback_query.from_user.id != me.id:
        return await callback_query.answer("🚫 Akses Ditolak.", show_alert=True)

    # 1. Navigasi Kategori (Back to Main)
    if data == "back_to_main":
        await callback_query.answer()
        text = "🌌 **Nebula Engine Dashboard**\n━━━━━━━━━━━━━━━━━━━━\nPilih kategori modul di bawah ini:"
        await callback_query.edit_message_text(text, reply_markup=await get_main_help_menu())

    # 2. Navigasi Daftar Plugin dalam Kategori
    elif data.startswith("cat_"):
        await callback_query.answer()
        category = data.replace("cat_", "")
        text = f"📦 **Modul Kategori:** `{category}`\n━━━━━━━━━━━━━━━━━━━━\nPilih plugin (nama file) untuk melihat detail perintah."
        markup = await get_plugin_list_markup(category)
        if markup:
            await callback_query.edit_message_text(text, reply_markup=markup)
        else:
            await callback_query.answer("Belum ada plugin di kategori ini.", show_alert=True)

    # 3. Navigasi Detail Perintah di dalam Plugin
    elif data.startswith("plug_"):
        await callback_query.answer()
        parts = data.split("_", 2)
        category, plugin_name = parts[1], parts[2]
        
        commands_info = CMD_HELP.get(category, {}).get(plugin_name, {})
        text = f"📦 **Plugin:** `{plugin_name}`\n"
        text += f"📂 **Kategori:** `{category}`\n"
        text += "━━━━━━━━━━━━━━━━━━━━\n"
        for cmd, info in commands_info.items():
            text += f"• `.{cmd}` : {info}\n"
        
        markup = await get_plugin_detail_markup(client.parent, category, plugin_name)
        await callback_query.edit_message_text(text, reply_markup=markup)

    # 4. Logika Toggle Khusus
    elif data.startswith("toggle_"):
        key = data.replace("toggle_", "")
        await callback_query.answer("⚡ Diupdate...")
        
        # Penanganan Toggle Dinamis
        if key == "lang_switch":
            current = await client.parent.db.get("lang", "id")
            await client.parent.db.set("lang", "en" if current == "id" else "id")
            await callback_query.edit_message_reply_markup(reply_markup=await get_plugin_detail_markup(client.parent, "System", "system"))
        else:
            current = await client.parent.db.get(key, (True if key == "anti_delete" else False))
            await client.parent.db.set(key, not current)
            
            # Coba deteksi kategori untuk refresh otomatis (Paling sering di Security)
            # Ini bisa dioptimalkan dengan menyimpan state di callback_data jika perlu
            await callback_query.edit_message_reply_markup(reply_markup=await get_plugin_detail_markup(client.parent, "Security", "pmpermit" if "pm" in key else "antispam"))

    # 5. Kontrol & Info
    elif data == "close_db":
        await callback_query.answer("🗑 Ditutup.")
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
