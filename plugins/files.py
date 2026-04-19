import os
from hydrogram import Client
from hydrogram.types import Message
from core.decorators import on_cmd
from utils.shell import async_exec


@Client.on_message(on_cmd("ls", category="System", info="List file di direktori saat ini di VPS."))
async def list_files(client, message: Message):
    path = message.text.split(None, 1)[1] if len(message.command) > 1 else "."
    res = await async_exec(f"ls -lh {path}")
    await client.fast_edit(message, f"📂 **Directory: {path}**\n\n```text\n{res}```")


@Client.on_message(on_cmd("rm", category="System", info="Hapus file di VPS (Hati-hati!)."))
async def remove_file(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "✦ Tentukan file yang mau dihapus.")

    file_path = message.command[1]
    if os.path.exists(file_path):
        os.remove(file_path)
        await client.fast_edit(message, f"✅ **Berhasil dihapus:** `{file_path}`")
    else:
        await client.fast_edit(message, f"❌ **File tidak ditemukan:** `{file_path}`")


@Client.on_message(on_cmd("get", category="System", info="Ambil file dari VPS ke Telegram."))
async def get_file_vps(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "✦ Tentukan file yang mau diambil.")

    file_path = message.command[1]
    if os.path.exists(file_path):
        status = await client.fast_edit(message, "⏳ `Mengunggah file...`")
        await client.send_document(message.chat.id, file_path)
        await status.delete()
    else:
        await client.fast_edit(message, f"❌ **File tidak ditemukan:** `{file_path}`")
