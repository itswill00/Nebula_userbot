from hydrogram import Client
from hydrogram.types import Message
from core.decorators import on_cmd


@Client.on_message(on_cmd("sudo", category="Security", info="Tanda atau hapus user dari daftar Sudo."))
async def manage_sudo(client, message: Message):
    user_id = None
    
    # 1. Cek dari Reply
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    # 2. Cek dari Argumen
    elif len(message.command) > 1:
        try:
            user_id = int(message.command[1])
        except ValueError:
            return await client.fast_edit(message, "⚠️ **ID User harus berupa angka.**")
    else:
        return await client.fast_edit(message, "⚠️ **Balas pesan user atau masukkan ID untuk dikelola.**")

    # Jangan biarkan pemilik menghapus dirinya sendiri dari logika (walaupun filter.me selalu True)
    if user_id == (await client.get_me()).id:
        return await client.fast_edit(message, "👤 **Anda adalah pemilik bot ini.**")

    sudo_users = await client.db.get("sudo_users", [])
    
    if user_id in sudo_users:
        sudo_users.remove(user_id)
        action = "dihapus dari"
    else:
        sudo_users.append(user_id)
        action = "ditambahkan ke"

    await client.db.set("sudo_users", sudo_users)
    await client.fast_edit(message, f"👤 **User `{user_id}` telah {action} daftar Sudo.**")


@Client.on_message(on_cmd(["sudos", "fullsudo"], category="Security", info="Lihat daftar semua user Sudo."))
async def list_sudos(client, message: Message):
    sudo_users = await client.db.get("sudo_users", [])
    
    if not sudo_users:
        return await client.fast_edit(message, "📭 **Tidak ada user Sudo yang terdaftar.**")

    text = "🛡️ **Nebula Sudo Users**\n\n"
    for uid in sudo_users:
        text += f"• `{uid}`\n"
    
    await client.fast_edit(message, text)
