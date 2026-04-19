from hydrogram import Client, filters
from hydrogram.types import Message

PREFIX = "."


@Client.on_message(filters.private & ~filters.me & ~filters.bot, group=-1)
async def pm_guard(client, message: Message):
    """Sistem proteksi pesan pribadi otomatis."""
    user_id = message.from_user.id
    is_approved = await client.db.get(f"approve_{user_id}", False)

    if not is_approved:
        warned = await client.db.get(f"warned_{user_id}", False)
        if not warned:
            await message.reply(
                "🛡 **Nebula PM Security**\n\n"
                "Halo! Anda belum disetujui oleh pemilik akun ini. "
                "Pesan Anda akan diabaikan hingga persetujuan diberikan."
            )
            await client.db.set(f"warned_{user_id}", True)
        return

# --- GLOBAL BAN SYSTEM ---


@Client.on_message(filters.group & ~filters.me, group=-2)
async def check_gban(client, message: Message):
    """Mengecek setiap user yang masuk/kirim pesan terhadap daftar G-Ban."""
    if not message.from_user:
        return

    gban_list = await client.db.get("gban_list", [])
    user_id = message.from_user.id

    if user_id in gban_list:
        try:
            await client.ban_chat_member(message.chat.id, user_id)
            await message.delete()
        except Exception:
            pass  # Gagal ban karena bot bukan admin di grup tersebut


@Client.on_message(filters.command("gban", prefixes=PREFIX) & filters.me)
async def gban_user(client, message: Message):
    """Memasukkan user ke daftar Global Ban."""
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        user_id = int(message.command[1])
    else:
        return await message.edit("`Balas ke user atau berikan ID.`")

    gban_list = await client.db.get("gban_list", [])
    if user_id not in gban_list:
        gban_list.append(user_id)
        await client.db.set("gban_list", gban_list)
        await message.edit(f"🚫 `User {user_id} telah di-GBan secara global.`")
        # Coba ban di chat saat ini
        try:
            await client.ban_chat_member(message.chat.id, user_id)
        except Exception:
            pass
    else:
        await message.edit("`User sudah ada di daftar G-Ban.`")


@Client.on_message(filters.command("ungban", prefixes=PREFIX) & filters.me)
async def ungban_user(client, message: Message):
    """Menghapus user dari daftar Global Ban."""
    if len(message.command) < 2:
        return await message.edit("`Berikan ID user.`")

    user_id = int(message.command[1])
    gban_list = await client.db.get("gban_list", [])

    if user_id in gban_list:
        gban_list.remove(user_id)
        await client.db.set("gban_list", gban_list)
        await message.edit(f"✅ `User {user_id} telah dihapus dari daftar G-Ban.`")
    else:
        await message.edit("`User tidak ditemukan di daftar G-Ban.`")
