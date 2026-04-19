from hydrogram import Client
from hydrogram.types import Message
from core.decorators import on_cmd


@Client.on_message(on_cmd("info", category="Scraper", info="Ambil informasi lengkap user atau grup."))
async def get_info(client, message: Message):
    status = await client.fast_edit(message, "⏳ `Mengambil data...`")

    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    chat = message.chat

    # Jika membalas pesan user
    if target:
        info = (
            f"👤 **USER INFORMATION**\n\n"
            f"**Nama:** `{target.first_name}`\n"
            f"**ID:** `{target.id}`\n"
            f"**Username:** `@{target.username or '-'}`\n"
            f"**DC ID:** `{target.dc_id or '?'}`\n"
            f"**Status:** `{'Bot' if target.is_bot else 'Manusia'}`\n"
            f"**Link:** [Permanen](tg://user?id={target.id})"
        )
    else:
        info = (
            f"📍 **CHAT INFORMATION**\n\n"
            f"**Judul:** `{chat.title}`\n"
            f"**ID:** `{chat.id}`\n"
            f"**Tipe:** `{chat.type}`\n"
            f"**Username:** `@{chat.username or '-'}`"
        )

    await status.edit(info)


@Client.on_message(on_cmd("id", category="Scraper", info="Cek ID chat atau user balasan secara instan."))
async def get_id(client, message: Message):
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        await client.fast_edit(message, f"✦ **User ID:** `{target.id}`\n✦ **Chat ID:** `{message.chat.id}`")
    else:
        await client.fast_edit(message, f"✦ **Chat ID:** `{message.chat.id}`")
