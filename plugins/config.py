from hydrogram import Client, filters
from hydrogram.types import Message

@Client.on_message(filters.command("lang", prefixes=".") & filters.me)
async def set_language(client, message: Message):
    """Mengubah bahasa bot secara global."""
    if len(message.command) < 2:
        return await message.edit("`Format: .lang <id|en>`")
    
    new_lang = message.command[1].lower()
    if new_lang in ["id", "en"]:
        await client.db.set("lang", new_lang)
        success_msg = await client.get_string("SET_LANG_SUCCESS")
        await message.edit(success_msg)
    else:
        err_msg = await client.get_string("SET_LANG_INVALID")
        await message.edit(err_msg)

@Client.on_message(filters.command("setting", prefixes=".") & filters.me)
async def set_config(client, message: Message):
    """Mengubah pengaturan internal bot."""
    if len(message.command) < 3:
        # Menampilkan daftar pengaturan saat ini
        prefix = await client.db.get("prefix", ".")
        anti_delete = await client.db.get("anti_delete", True)
        anti_edit = await client.db.get("anti_edit", True)
        lang = await client.db.get("lang", "id")
        
        info = (
            "⚙️ **Nebula Config Manager**\n\n"
            f"**Language:** `{lang}`\n"
            f"**Prefix:** `{prefix}`\n"
            f"**Anti-Delete:** `{anti_delete}`\n"
            f"**Anti-Edit:** `{anti_edit}`\n\n"
            "Gunakan `.setting <key> <value>` untuk mengubah."
        )
        return await message.edit(info)
    
    key = message.command[1].lower()
    value = message.text.split(None, 2)[2]
    
    # Handle boolean conversion
    if value.lower() in ["true", "yes", "on"]:
        value = True
    elif value.lower() in ["false", "no", "off"]:
        value = False
        
    await client.db.set(key, value)
    success = await client.get_string("SET_VALUE_SUCCESS")
    await message.edit(success.format(key=key, value=value))

@Client.on_message(filters.command("restart", prefixes=".") & filters.me)
async def restart_bot(client, message: Message):
    """Restart bot (hanya berfungsi di Docker dengan restart: always)."""
    await message.edit("`Bot is restarting...`")
    import os
    os._exit(0)
