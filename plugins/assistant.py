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
    
    text = await client.get_string("DASHBOARD_TEXT")
    
    # Ambil status saat ini
    is_ad = await client.db.get("anti_delete", True)
    is_as = await client.db.get("antispam", False)
    lang = await client.db.get("lang", "id")

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
        await client.assistant.send_message(
            message.chat.id, 
            text, 
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await message.delete()
    except Exception:
        # Fallback jika Bot tidak ada di chat
        await client.fast_edit(message, f"{text}\n\n⚠️ **Tombol nggak muncul.** Coba `/start` dulu di bot asisten kamu atau masukin dia ke grup ini.")

# Handler untuk Assistant Bot (CallbackQuery)
async def assistant_callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    user_me = await client.parent.get_me()
    
    if callback_query.from_user.id != user_me.id:
        return await callback_query.answer("Akses Ditolak.", show_alert=True)

    if data.startswith("conf_"):
        key = data.replace("conf_", "")
        
        if key == "lang_switch":
            current = await client.parent.db.get("lang", "id")
            new_val = "en" if current == "id" else "id"
            await client.parent.db.set("lang", new_val)
        else:
            current = await client.parent.db.get(key, True)
            new_val = not current
            await client.parent.db.set(key, new_val)
        
        # Refresh Dashboard
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
        
        text = await client.parent.get_string("DASHBOARD_TEXT")
        await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        await callback_query.answer("Pengaturan diperbarui!")

    elif data == "close_db":
        await callback_query.message.delete()

# --- CONTACT BOT LOGIC ---
async def assistant_contact_handler(client, message: Message):
    master = await client.parent.get_me()
    if message.from_user.id == master.id:
        return

    text = await client.parent.get_string("CONTACT_MSG")
    await client.parent.send_message(
        "me",
        text.format(
            name=message.from_user.first_name,
            id=message.from_user.id,
            text=message.text or "[Media]"
        )
    )
    sent_text = await client.parent.get_string("CONTACT_SENT")
    await message.reply(sent_text)
