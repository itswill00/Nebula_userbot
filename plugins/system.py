import time
import os
import psutil
from hydrogram import Client, filters
from hydrogram.types import Message
from utils.shell import async_exec

# Menggunakan dekorator baru
@Client.on_cmd("sh", category="System", info="Eksekusi terminal (bash).")
async def shell_runner(client, message: Message):
    if len(message.command) < 2:
        return await message.edit("`Coba kasih perintah terminalnya apa.`")
    cmd = message.text.split(maxsplit=1)[1]
    await message.edit("`Siap, lagi aku kerjain...`")
    result = await async_exec(cmd)
    await message.edit(f"**$** `{cmd}`\n\n**Output:**\n```bash\n{result}\n```")

@Client.on_cmd("sys", category="System", info="Pantau kesehatan server.")
async def system_stats(client, message: Message):
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    stats = (
        "📊 **Laporan Kondisi Server:**\n\n"
        f"**Beban CPU:** `{cpu}%` (Lagi santai)" if cpu < 50 else f"**Beban CPU:** `{cpu}%` (Lagi kerja keras nih!)"
        f"\n**Pemakaian RAM:** `{mem.percent}%` dari total `{mem.total // (1024**2)}MB`"
        f"\n**Sisa Disk:** `{100 - disk.percent}%` lagi kosong."
    )
    await client.fast_edit(message, stats)

@Client.on_cmd("ping", category="System", info="Tes latensi bot ke Telegram.")
async def ping_pong(client, message: Message):
    start_time = time.time()
    await message.edit("`Bentar, aku cek dulu...`")
    end_time = time.time()
    latency = round((end_time - start_time) * 1000, 2)
    await message.edit(f"**Pong!**\nLatensi aku: `{latency}ms`")

@Client.on_cmd("update", category="System", info="Perbarui bot ke versi terbaru.")
async def update_bot(client, message: Message):
    await message.edit("`Bentar, aku cek dulu ya ke GitHub kalau ada pembaruan...`")
    out = await async_exec("git pull")
    if "Already up to date" in out:
        return await message.edit(f"✅ **Beres!** Aku udah versi paling baru kok.")
    await message.edit(f"🔄 **Ada pembaruan nih!**\n`{out}`\n\n`Aku update sekarang terus aku restart ya...`")
    os._exit(0)
