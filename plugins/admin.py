import asyncio
from hydrogram import Client
from hydrogram.types import Message, ChatPermissions
from hydrogram.errors import FloodWait
from core.decorators import on_cmd

@Client.on_message(on_cmd("purge", category="Admin", info="Hapus banyak pesan sekaligus (Balas ke pesan awal)."))
async def purge_messages(client, message: Message):
    if not message.reply_to_message:
        return await client.fast_edit(message, "✦ Balas ke pesan awal sebagai batas hapus.")
    
    chat_id = message.chat.id
    message_ids = range(message.reply_to_message.id, message.id)
    
    await message.delete()
    count = 0
    try:
        for i in range(0, len(message_ids), 100):
            batch = message_ids[i:i+100]
            await client.delete_messages(chat_id, batch)
            count += len(batch)
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        return await client.send_message("me", f"❌ **Purge Error:** `{str(e)}`")

    status = await client.send_message(chat_id, f"✅ **Purge Selesai**\n\nTotal `{count}` pesan berhasil dilenyapkan.")
    await asyncio.sleep(3)
    await status.delete()

@Client.on_message(on_cmd("ban", category="Admin", info="Blokir permanen user dari grup."))
async def ban_user(client, message: Message):
    replied = message.reply_to_message
    if not replied:
        return await client.fast_edit(message, "✦ Balas ke user yang mau ditendang permanen.")
    user = replied.from_user
    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await client.fast_edit(message, f"🛡 **Tindakan Keras**\n\nUser `{user.first_name}` telah dibanned dari grup ini.")
    except Exception as e:
        await client.fast_edit(message, f"❌ **Gagal Ban:** `{str(e)}`")

@Client.on_message(on_cmd("kick", category="Admin", info="Keluarkan user dari grup (Bisa masuk lagi)."))
async def kick_user(client, message: Message):
    replied = message.reply_to_message
    if not replied:
        return await client.fast_edit(message, "✦ Balas ke user yang mau dikick sementara.")
    user = replied.from_user
    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await client.unban_chat_member(message.chat.id, user.id)
        await client.fast_edit(message, f"🛡 **Kicked**\n\nUser `{user.first_name}` telah dikeluarkan sementara.")
    except Exception as e:
        await client.fast_edit(message, f"❌ **Gagal Kick:** `{str(e)}`")

@Client.on_message(on_cmd("mute", category="Admin", info="Bungkam user di grup."))
async def mute_user(client, message: Message):
    replied = message.reply_to_message
    if not replied:
        return await client.fast_edit(message, "✦ Balas ke user yang mau dibungkam.")
    user = replied.from_user
    try:
        await client.restrict_chat_member(message.chat.id, user.id, ChatPermissions(can_send_messages=False))
        await client.fast_edit(message, f"🔇 **Bungkam**\n\nUser `{user.first_name}` kehilangan hak bicara.")
    except Exception as e:
        await client.fast_edit(message, f"❌ **Gagal Mute:** `{str(e)}`")

@Client.on_message(on_cmd("pin", category="Admin", info="Sematkan pesan di grup."))
async def pin_message(client, message: Message):
    replied = message.reply_to_message
    if not replied:
        return await client.fast_edit(message, "✦ Balas pesan yang mau disematkan.")
    try:
        await replied.pin(notify=True)
        await client.fast_edit(message, "📌 **Pesan berhasil disematkan!**")
    except Exception as e:
        await client.fast_edit(message, f"❌ **Gagal menyematkan pesan:** `{str(e)}`")

@Client.on_message(on_cmd("unpin", category="Admin", info="Lepas sematan pesan di grup."))
async def unpin_message(client, message: Message):
    replied = message.reply_to_message
    if not replied:
        return await client.fast_edit(message, "✦ Balas pesan yang sematannya mau dilepas.")
    try:
        await replied.unpin()
        await client.fast_edit(message, "📌 **Sematan pesan telah dilepas!**")
    except Exception as e:
        await client.fast_edit(message, f"❌ **Gagal melepas sematan:** `{str(e)}`")

@Client.on_message(on_cmd("zombies", category="Admin", info="Bersihkan grup dari akun yang sudah dihapus (Deleted Accounts)."))
async def clean_zombies(client, message: Message):
    if message.chat.type in ["private", "bot"]:
        return await client.fast_edit(message, "✦ Perintah ini cuma bisa dipakai di Grup/Channel.")
    
    await client.fast_edit(message, "⏳ `Memindai anggota grup untuk mencari akun Zombie...`")
    zombies = 0
    async for member in client.get_chat_members(message.chat.id):
        if member.user.is_deleted:
            try:
                await client.ban_chat_member(message.chat.id, member.user.id)
                zombies += 1
            except:
                pass
            
    if zombies > 0:
        await client.fast_edit(message, f"✅ **Operasi Bersih-bersih Selesai**\n\nBerhasil membasmi `{zombies}` akun Zombie.")
    else:
        await client.fast_edit(message, "✅ **Grup Bersih**\n\nTidak ada akun Zombie yang ditemukan.")
