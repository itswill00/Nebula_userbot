import os
import sys
from hydrogram import Client
from hydrogram.types import Message
from core.decorators import on_cmd


@Client.on_message(on_cmd("install", category="System", info="Pasang plugin baru dengan membalas file .py."))
async def install_plugin(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await client.fast_edit(message, "⚠️ **Balas ke file `.py` untuk memasang plugin.**")

    file = message.reply_to_message.document
    if not file.file_name.endswith(".py"):
        return await client.fast_edit(message, "⚠️ **Hanya file `.py` yang didukung.**")

    plugin_name = file.file_name
    plugin_path = os.path.join("plugins", plugin_name)

    if os.path.exists(plugin_path):
        return await client.fast_edit(message, f"⚠️ **Plugin `{plugin_name}` sudah ada.**")

    await client.fast_edit(message, f"📥 **Mengunduh `{plugin_name}`...**")
    download_path = await client.download_media(message.reply_to_message, file_name=plugin_path)

    if download_path:
        await client.fast_edit(message, f"✅ **Berhasil memasang `{plugin_name}`!**\n\n🔄 **Merestart Nebula untuk menerapkan...**")
        
        # Simpan status untuk pemulihan pasca restart
        await client.db.set("restart_info", {
            "chat_id": message.chat.id,
            "msg_id": message.id
        })
        
        # Restart
        os.execl(sys.executable, sys.executable, "main.py")
    else:
        await client.fast_edit(message, "❌ **Gagal mengunduh plugin.**")


@Client.on_message(on_cmd("uninstall", category="System", info="Hapus plugin yang sudah terpasang."))
async def uninstall_plugin(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "⚠️ **Masukkan nama plugin untuk dihapus.**\nContoh: `.uninstall custom_mod` (tanpa .py)")

    plugin_name = message.command[1]
    if not plugin_name.endswith(".py"):
        plugin_name += ".py"

    plugin_path = os.path.join("plugins", plugin_name)

    if not os.path.exists(plugin_path):
        return await client.fast_edit(message, f"❌ **Plugin `{plugin_name}` tidak ditemukan.**")

    try:
        os.remove(plugin_path)
        await client.fast_edit(message, f"🗑️ **Plugin `{plugin_name}` berhasil dihapus.**\n\n🔄 **Merestart Nebula...**")
        
        # Simpan status untuk pemulihan
        await client.db.set("restart_info", {
            "chat_id": message.chat.id,
            "msg_id": message.id
        })
        
        # Restart
        os.execl(sys.executable, sys.executable, "main.py")
    except Exception as e:
        await client.fast_edit(message, f"❌ **Gagal menghapus plugin:**\n`{e}`")


@Client.on_message(on_cmd("plugins", category="System", info="Lihat daftar semua plugin yang aktif."))
async def list_plugins(client, message: Message):
    plugin_list = [f for f in os.listdir("plugins") if f.endswith(".py") and not f.startswith("_")]
    
    if not plugin_list:
        return await client.fast_edit(message, "📭 **Tidak ada plugin kustom yang terdeteksi.**")

    text = f"🔌 **Nebula Active Plugins ({len(plugin_list)})**\n\n"
    for plugin in sorted(plugin_list):
        text += f"• `{plugin.replace('.py', '')}`\n"
    
    await client.fast_edit(message, text)


@Client.on_message(on_cmd("disable", category="System", info="Matikan plugin tertentu di chat ini."))
async def disable_chat_plugin(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "⚠️ **Masukkan nama plugin untuk dimatikan.**")

    plugin_name = message.command[1]
    chat_id = message.chat.id
    
    disabled = await client.db.get(f"disabled_plugins:{chat_id}", [])
    if plugin_name not in disabled:
        disabled.append(plugin_name)
        await client.db.set(f"disabled_plugins:{chat_id}", disabled)
    
    await client.fast_edit(message, f"❌ **Plugin `{plugin_name}` dinonaktifkan di chat ini.**")


@Client.on_message(on_cmd("enable", category="System", info="Aktifkan kembali plugin di chat ini."))
async def enable_chat_plugin(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "⚠️ **Masukkan nama plugin untuk diaktifkan.**")

    plugin_name = message.command[1]
    chat_id = message.chat.id
    
    disabled = await client.db.get(f"disabled_plugins:{chat_id}", [])
    if plugin_name in disabled:
        disabled.remove(plugin_name)
        await client.db.set(f"disabled_plugins:{chat_id}", disabled)
    
    await client.fast_edit(message, f"✅ **Plugin `{plugin_name}` diaktifkan kembali di chat ini.**")
