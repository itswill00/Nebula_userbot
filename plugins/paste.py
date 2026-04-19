import aiohttp
from hydrogram import Client
from hydrogram.types import Message
from core.decorators import on_cmd


@Client.on_message(on_cmd("paste", category="Utilitas", info="Upload teks/kode ke Nekobin."))
async def paste_text(client, message: Message):
    text = ""
    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    else:
        return await client.fast_edit(message, "✦ Berikan teks atau balas ke pesan teks.")

    await client.fast_edit(message, "⏳ `Mengunggah ke Nekobin...`")

    async with aiohttp.ClientSession() as session:
        async with session.post("https://nekobin.com/api/documents", json={"content": text}) as resp:
            if resp.status == 201:
                data = await resp.json()
                key = data["result"]["key"]
                url = f"https://nekobin.com/{key}"
                await client.fast_edit(
                    message,
                    f"✅ **Teks Berhasil Diunggah!**\n\n🔗 [Buka Tautan Nekobin]({url})",
                    disable_web_page_preview=True
                )
            else:
                await client.fast_edit(message, "❌ **Gagal mengunggah ke Nekobin.**")
