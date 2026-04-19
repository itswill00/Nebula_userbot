import asyncio
from hydrogram import Client, filters
from hydrogram.types import Message
from hydrogram.errors import FloodWait

PREFIX = "."

@Client.on_message(filters.command("purge", prefixes=PREFIX) & filters.me)
async def purge_messages(client, message: Message):
    """Menghapus banyak pesan sekaligus (Purge)."""
    if not message.reply_to_message:
        return await message.edit("`Balas ke pesan awal untuk purge.`")
    
    chat_id = message.chat.id
    message_ids = range(message.reply_to_message.id, message.id)
    
    await message.delete()
    count = 0
    try:
        # Batch delete untuk efisiensi API
        for i in range(0, len(message_ids), 100):
            batch = message_ids[i:i+100]
            await client.delete_messages(chat_id, batch)
            count += len(batch)
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        return await client.send_message("me", f"**Purge Error:** `{str(e)}`")

    status = await client.send_message(chat_id, f"**Purge Selesai:** `{count}` pesan dihapus.")
    await asyncio.sleep(3)
    await status.delete()

@Client.on_message(filters.command(["ban", "kick", "mute"], prefixes=PREFIX) & filters.me)
async def admin_actions(client, message: Message):
    """Aksi admin tunggal (Ban/Kick/Mute)."""
    cmd = message.command[0]
    replied = message.reply_to_message
    
    if not replied:
        return await message.edit("`Balas ke user.`")
    
    user_id = replied.from_user.id
    chat_id = message.chat.id
    
    try:
        if cmd == "ban":
            await client.ban_chat_member(chat_id, user_id)
        elif cmd == "kick":
            await client.ban_chat_member(chat_id, user_id)
            await client.unban_chat_member(chat_id, user_id)
        elif cmd == "mute":
            from hydrogram.types import ChatPermissions
            await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
        
        await message.edit(f"**Action:** `{cmd.upper()}`\n**User:** `{user_id}`")
    except Exception as e:
        await message.edit(f"**Admin Error:** `{str(e)}`")
