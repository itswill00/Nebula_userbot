import time
import asyncio
from hydrogram import Client, filters, enums
from hydrogram.types import Message
from core.decorators import on_cmd, brain_rule
from core.brain import Action, Intent

# Cache untuk throttling (user_id: last_replied_time)
AFK_REPLY_CACHE = {}
# Cache untuk cleanup (chat_id: last_reply_message_id)
AFK_MSG_CACHE = {}


def format_duration(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    parts = []
    if days > 0:
        parts.append(f"{days} hari")
    if hours > 0:
        parts.append(f"{hours} jam")
    if minutes > 0:
        parts.append(f"{minutes} menit")
    if seconds > 0 or not parts:
        parts.append(f"{seconds} detik")

    return " ".join(parts)


@Client.on_message(on_cmd("afk", category="Identity", info="Aktifkan mode AFK (Away From Keyboard)."))
async def set_afk(client, message: Message):
    reason = message.text.split(None, 1)[1] if len(
        message.command) > 1 else "Lagi sibuk, jangan diganggu dulu ya."
    afk_time = time.time()
    media_id = None
    media_type = None

    # Dukungan Media: Jika membalas pesan media
    if message.reply_to_message:
        reply = message.reply_to_message
        if reply.photo:
            media_id = reply.photo.file_id
            media_type = "photo"
        elif reply.sticker:
            media_id = reply.sticker.file_id
            media_type = "sticker"
        elif reply.animation:
            media_id = reply.animation.file_id
            media_type = "animation"

    await client.db.set("afk", {
        "is_afk": True,
        "reason": reason,
        "time": afk_time,
        "media_id": media_id,
        "media_type": media_type
    })

    res = f"💤 **Mode AFK Aktif**\n\n**Alasan:** `{reason}`"
    if media_id:
        res += "\n*(Media tersimpan sebagai banner)*"

    await client.fast_edit(message, res)


@brain_rule
async def afk_brain_rule(client, ctx):
    afk_data = ctx["afk_data"]
    if not afk_data or not afk_data.get("is_afk"):
        return None

    message = ctx["message"]
    # Cek apakah di-tag atau di PM
    is_tagged = (
        message.mentioned
        or (
            message.reply_to_message
            and message.reply_to_message.from_user
            and message.reply_to_message.from_user.is_self
        )
    )

    is_private = (
        ctx["chat_type"] == enums.ChatType.PRIVATE
        or str(ctx["chat_type"]) == "ChatType.PRIVATE"
    )

    if is_private or is_tagged:
        user_id = ctx["user_id"]
        chat_id = message.chat.id
        now = ctx["time"]

        # Throttling: Cooldown 30 detik per user
        last_reply = AFK_REPLY_CACHE.get(user_id, 0)
        if now - last_reply < 30:
            return None

        AFK_REPLY_CACHE[user_id] = now

        uptime = round(now - afk_data.get("time", now))
        since = format_duration(uptime)

        res = (
            f"💤 **Maaf, Bos lagi AFK**\n\n"
            f"**Sejak:** `{since} lalu`\n"
            f"**Alasan:** `{afk_data.get('reason')}`"
        )

        async def execute_afk():
            # Cleanup: Hapus balasan AFK sebelumnya di chat ini jika ada
            prev_msg_id = AFK_MSG_CACHE.get(chat_id)
            if prev_msg_id:
                try:
                    await client.delete_messages(chat_id, prev_msg_id)
                except Exception:
                    pass

            # Kirim Balasan (dengan Media jika ada)
            media_id = afk_data.get("media_id")
            media_type = afk_data.get("media_type")

            try:
                if media_id:
                    if media_type == "photo":
                        rep = await message.reply_photo(media_id, caption=res)
                    elif media_type == "sticker":
                        # Sticker tidak bisa dikasih caption di reply_sticker (bot API limitation/lib check)
                        # Tapi kita kirim sticker lalu res sebagai pesan terpisah atau reply
                        rep = await message.reply_sticker(media_id)
                        await message.reply(res)
                    elif media_type == "animation":
                        rep = await message.reply_animation(media_id, caption=res)
                    else:
                        rep = await message.reply(res)
                else:
                    rep = await message.reply(res)

                # Simpan message id untuk cleanup selanjutnya
                AFK_MSG_CACHE[chat_id] = rep.id
            except Exception:
                pass

        return Action(intent=Intent.REPLY, plugin_name="afk", execute=execute_afk)
    return None


@Client.on_message(filters.me & filters.outgoing, group=3)
async def auto_unafk(client, message: Message):
    # Jangan matikan AFK jika yang dikirim adalah perintah .afk itu sendiri
    if message.text and (message.text.startswith(".afk") or message.text.startswith("/afk")):
        return

    afk_data = await client.db.get("afk", {"is_afk": False})
    if afk_data.get("is_afk"):
        uptime = round(time.time() - afk_data.get("time", time.time()))
        since = format_duration(uptime)

        await client.db.set("afk", {"is_afk": False})

        status = await client.send_message(
            "me",
            f"✅ **Mode AFK dimatikan.**\n"
            f"Selamat datang kembali, Bos!\n\n"
            f"**Total AFK:** `{since}`"
        )

        AFK_REPLY_CACHE.clear()
        AFK_MSG_CACHE.clear()

        await asyncio.sleep(5)
        await status.delete()
