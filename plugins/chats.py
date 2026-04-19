import asyncio
from hydrogram import Client
from hydrogram.types import Message
from core.decorators import on_cmd


@Client.on_message(on_cmd("gcast", category="Admin", info="Siaran pesan global ke semua grup."))
async def global_broadcast(client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        return await client.fast_edit(message, "✦ Kasih teks atau balas ke pesan yang mau disiarin.")

    status = await client.fast_edit(message, "⏳ `Memulai siaran global...`")

    count = 0
    error = 0
    # Ambil semua chat tipe grup dan supergrup
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["group", "supergroup"]:
            try:
                if message.reply_to_message:
                    await message.reply_to_message.copy(dialog.chat.id)
                else:
                    await client.send_message(dialog.chat.id, message.text.split(None, 1)[1])
                count += 1
                await asyncio.sleep(0.3)  # Anti flood
            except Exception:
                error += 1

    await status.edit(f"✅ **Siaran Selesai**\n\n**Berhasil:** `{count}` grup\n**Gagal:** `{error}` grup")


@Client.on_message(on_cmd("tagall", category="Admin", info="Tag seluruh anggota grup (max 100)."))
async def tag_all_members(client, message: Message):
    status = await client.fast_edit(message, "⏳ `Memulai penandaan massal...`")

    tag_text = message.text.split(None, 1)[1] if len(
        message.command) > 1 else "Woy, bangun!"
    mentions = ""
    count = 0

    async for member in client.get_chat_members(message.chat.id, limit=100):
        if not member.user.is_bot:
            mentions += f"[{member.user.first_name}](tg://user?id={member.user.id}) "
            count += 1
            if count % 5 == 0:
                await client.send_message(message.chat.id, f"{tag_text}\n\n{mentions}")
                mentions = ""
                await asyncio.sleep(1)

    await status.delete()
