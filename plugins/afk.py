import time
import asyncio
from hydrogram import Client, filters
from hydrogram.types import Message
from core.decorators import on_cmd

# In-memory cache untuk anti-spam (user_id: last_replied_time)
AFK_REPLY_CACHE = {}

def format_duration(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    parts = []
    if days > 0: parts.append(f"{days} hari")
    if hours > 0: parts.append(f"{hours} jam")
    if minutes > 0: parts.append(f"{minutes} menit")
    if seconds > 0 or not parts: parts.append(f"{seconds} detik")
    
    return " ".join(parts)

@Client.on_message(on_cmd("afk", category="Identity", info="Aktifkan mode AFK (Away From Keyboard)."))
async def set_afk(client, message: Message):
    reason = message.text.split(None, 1)[1] if len(message.command) > 1 else "Lagi sibuk, jangan diganggu dulu ya."
    afk_time = time.time()
    
    await client.db.set("afk", {"is_afk": True, "reason": reason, "time": afk_time})
    
    await client.fast_edit(message, f"💤 **Mode AFK Aktif**\n\n**Alasan:** `{reason}`")

@Client.on_message(filters.all & ~filters.me, group=2)
async def afk_handler(client, message: Message):
    afk_data = await client.db.get("afk", {"is_afk": False})
    if not afk_data.get("is_afk"):
        return

    # Cek apakah di-tag atau di PM
    is_tagged = message.mentioned or (message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.is_self)
    
    if message.chat.type == "private" or is_tagged:
        user_id = message.from_user.id if message.from_user else message.chat.id
        now = time.time()
        
        # Throttling: Cooldown 30 detik per user/chat
        last_reply = AFK_REPLY_CACHE.get(user_id, 0)
        if now - last_reply < 30:
            return
            
        AFK_REPLY_CACHE[user_id] = now
        
        uptime = round(now - afk_data.get("time", now))
        since = format_duration(uptime)

        res = f"💤 **Maaf, Bos lagi AFK**\n\n**Sejak:** `{since} lalu`\n**Alasan:** `{afk_data.get('reason')}`"
        await message.reply(res)

@Client.on_message(filters.me & filters.outgoing, group=3)
async def auto_unafk(client, message: Message):
    # Jangan matikan AFK jika yang dikirim adalah perintah .afk itu sendiri
    if message.text and (message.text.startswith(".afk") or message.text.startswith("/afk")):
        return
        
    afk_data = await client.db.get("afk", {"is_afk": False})
    if afk_data.get("is_afk"):
        await client.db.set("afk", {"is_afk": False})
        status = await client.send_message("me", "✅ **Mode AFK dimatikan.** Selamat datang kembali, Bos!")
        AFK_REPLY_CACHE.clear()
        await asyncio.sleep(3)
        await status.delete()
