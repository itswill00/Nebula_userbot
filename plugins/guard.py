from hydrogram import Client
from hydrogram.types import Message, ChatMemberUpdated
from core.decorators import on_cmd
import logging

LOGS = logging.getLogger("Nebula")


@Client.on_message(on_cmd("gban", category="Keamanan", info="Blokir user secara global dari semua grup."))
async def gban_user(client, message: Message):
    replied = message.reply_to_message
    if not replied:
        return await client.fast_edit(message, "✦ Balas ke user yang mau dibanned global.")

    user = replied.from_user
    if user.is_self:
        return await client.fast_edit(message, "❌ Tidak bisa gban diri sendiri.")

    gban_list = await client.db.get("gban_list", [])
    if user.id not in gban_list:
        gban_list.append(user.id)
        await client.db.set("gban_list", gban_list)

    # Berusaha ban di chat saat ini
    try:
        await client.ban_chat_member(message.chat.id, user.id)
    except Exception:
        pass

    res_text = client.get_string("gban_success").format(user=user.mention)
    await client.fast_edit(message, res_text)


@Client.on_message(on_cmd("ungban", category="Keamanan", info="Lepas blokir global user."))
async def ungban_user(client, message: Message):
    replied = message.reply_to_message
    if not replied:
        return await client.fast_edit(message, "✦ Balas ke user yang mau di-ungban global.")

    user = replied.from_user
    gban_list = await client.db.get("gban_list", [])

    if user.id in gban_list:
        gban_list.remove(user.id)
        await client.db.set("gban_list", gban_list)

    res_text = client.get_string("ungban_success").format(user=user.mention)
    await client.fast_edit(message, res_text)


@Client.on_chat_member_updated()
async def gban_watcher(client, update: ChatMemberUpdated):
    """Otomatis tendang user gban yang join grup."""
    if not update.new_chat_member or update.new_chat_member.status in ["restricted", "left", "kicked"]:
        return

    user = update.new_chat_member.user
    gban_list = await client.db.get("gban_list", [])

    if user.id in gban_list:
        try:
            await client.ban_chat_member(update.chat.id, user.id)
            # Notifikasi ke log atau chat
            alert = client.get_string("guard_alert").format(user=user.mention)
            await client.send_message(update.chat.id, alert)
        except Exception as e:
            LOGS.error(f"Gagal menendang user gban: {e}")
