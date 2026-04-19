import logging
from hydrogram import Client, filters
from hydrogram.types import Message

PREFIX = "."

@Client.on_message(filters.private & ~filters.me & ~filters.bot)
async def pm_guard(client, message: Message):
    """Sistem proteksi pesan pribadi otomatis."""
    user_id = message.from_user.id
    is_approved = await client.db.get(f"approve_{user_id}", False)
    
    if not is_approved:
        # Kirim peringatan sekali saja per user
        warned = await client.db.get(f"warned_{user_id}", False)
        if not warned:
            await message.reply(
                "🛡 **Nebula PM Security**\n\n"
                "Halo! Anda belum disetujui oleh pemilik akun ini. "
                "Pesan Anda akan diabaikan hingga persetujuan diberikan."
            )
            await client.db.set(f"warned_{user_id}", True)
        # Mengabaikan pesan berikutnya
        return

@Client.on_message(filters.command("approve", prefixes=PREFIX) & filters.me)
async def approve_user(client, message: Message):
    """Menyetujui user di PM."""
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        user_id = message.command[1]
    else:
        return await message.edit("`Balas ke user atau berikan ID.`")
    
    await client.db.set(f"approve_{user_id}", True)
    await message.edit(f"`User {user_id} telah disetujui.`")

@Client.on_message(filters.command("disapprove", prefixes=PREFIX) & filters.me)
async def disapprove_user(client, message: Message):
    """Membatalkan persetujuan user di PM."""
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        user_id = message.command[1]
    else:
        return await message.edit("`Balas ke user atau berikan ID.`")
    
    await client.db.delete(f"approve_{user_id}")
    await message.edit(f"`Persetujuan user {user_id} dicabut.`")
