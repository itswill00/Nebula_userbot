from hydrogram import Client, filters
from hydrogram.types import Message


@Client.on_message(filters.command("save", prefixes=".") & filters.me)
async def save_data(client, message: Message):
    if len(message.command) < 3:
        return await message.edit("`Format: .save <key> <value>`")

    key = message.command[1]
    value = message.text.split(None, 2)[2]

    await client.db.set(key, value)
    await message.edit(f"`Berhasil menyimpan key: {key}`")


@Client.on_message(filters.command("get", prefixes=".") & filters.me)
async def get_data(client, message: Message):
    if len(message.command) < 2:
        return await message.edit("`Format: .get <key>`")

    key = message.command[1]
    val = await client.db.get(key)

    if val:
        await message.edit(f"**Key:** `{key}`\n**Value:** `{val}`")
    else:
        await message.edit("`Key tidak ditemukan.`")
