import time
from hydrogram import Client, filters
from hydrogram.types import Message
from core.decorators import on_cmd

# In-memory AFK state
AFK_DATA = {"is_afk": False, "reason": "", "time": 0}

@Client.on_message(on_cmd("afk", category="Identity", info="Aktifkan mode AFK (Away From Keyboard)."))
async def set_afk(client, message: Message):
    reason = message.text.split(None, 1)[1] if len(message.command) > 1 else "Lagi sibuk, jangan diganggu dulu ya."
    AFK_DATA["is_afk"] = True
    AFK_DATA["reason"] = reason
    AFK_DATA["time"] = time.time()
    
    await client.fast_edit(message, f"💤 **Mode AFK Aktif**\n\n**Alasan:** `{reason}`")

@Client.on_message(filters.all & ~filters.me, group=2)
async def afk_handler(client, message: Message):
    if not AFK_DATA["is_afk"]:
        return

    # Jika di PM atau di-tag di grup
    is_tagged = message.mentioned or (message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.is_self)
    
    if message.chat.type == "private" or is_tagged:
        now = time.time()
        uptime = round(now - AFK_DATA["time"])
        
        # Konversi detik ke format menit/jam
        if uptime < 60:
            since = f"{uptime} detik"
        else:
            since = f"{uptime // 60} menit"

        res = f"💤 **Maaf, Bos lagi AFK**\n\n**Sejak:** `{since} lalu`\n**Alasan:** `{AFK_DATA['reason']}`"
        await message.reply(res)

@Client.on_message(filters.me & filters.outgoing, group=3)
async def auto_unafk(client, message: Message):
    if AFK_DATA["is_afk"]:
        AFK_DATA["is_afk"] = False
        status = await client.send_message("me", "✅ **Mode AFK dimatikan.** Selamat datang kembali, Bos!")
        await asyncio.sleep(3)
        await status.delete()
