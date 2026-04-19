import os
import sys
import asyncio
from hydrogram import Client
from hydrogram.types import Message
from core.decorators import on_cmd


async def run_cmd(cmd):
    """Menjalankan perintah shell secara asinkron."""
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode().strip(), stderr.decode().strip()


@Client.on_message(on_cmd("restart", category="System", info="Restart bot Nebula."))
async def restart_bot(client, message: Message):
    msg = await client.fast_edit(message, "🚀 **Nebula sedang merestart...**\nMohon tunggu sebentar.")

    # Simpan konteks untuk pemulihan post-restart
    await client.db.set("restart_info", {
        "chat_id": message.chat.id,
        "msg_id": msg.id
    })

    # Eksekusi restart proses (mengganti proses saat ini dengan proses baru)
    print("🔄 Restarting Nebula...")
    # Pastikan menggunakan path yang benar (asumsi main.py di root)
    os.execl(sys.executable, sys.executable, "main.py")


@Client.on_message(on_cmd("update", category="System", info="Update bot Nebula dari repositori Git."))
async def update_bot(client, message: Message):
    msg = await client.fast_edit(message, "🔍 **Memeriksa pembaruan...**")

    # Ambil perubahan terbaru dari remote
    await run_cmd("wsl git fetch origin main")

    # Cek jumlah komit baru
    out, _ = await run_cmd("wsl git rev-list --count HEAD..origin/main")

    try:
        count = int(out) if out else 0
    except ValueError:
        count = 0

    if count == 0:
        return await msg.edit("🚀 **Nebula sudah menggunakan versi terbaru.**")

    # Ambil daftar perubahan (changelog)
    changelog, _ = await run_cmd("wsl git log HEAD..origin/main --oneline")

    update_text = (
        f"⬆️ **Ditemukan {count} pembaruan baru!**\n\n"
        f"**Changelog:**\n`{changelog}`\n\n"
        f"⚙️ **Sedang memperbarui...**"
    )
    await msg.edit(update_text)

    # Lakukan Pull
    pull_out, pull_err = await run_cmd("wsl git pull origin main")

    if pull_err and "error" in pull_err.lower():
        return await msg.edit(f"❌ **Gagal memperbarui:**\n`{pull_err}`")

    await msg.edit(f"✅ **Pembaruan selesai!**\n\n`{pull_out}`\n\n🔄 **Merestart Nebula...**")

    # Simpan status untuk pemulihan pasca restart
    await client.db.set("restart_info", {
        "chat_id": message.chat.id,
        "msg_id": msg.id
    })

    # Restart
    os.execl(sys.executable, sys.executable, "main.py")
