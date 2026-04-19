import time
import os
import psutil
from hydrogram import Client, filters
from hydrogram.types import Message
from utils.shell import async_exec

PREFIX = "."

@Client.on_message(filters.command("sh", prefixes=PREFIX) & filters.me)
async def shell_runner(client, message: Message):
    if len(message.command) < 2:
        return await message.edit("`Berikan perintah shell.`")
    cmd = message.text.split(maxsplit=1)[1]
    await message.edit("`Executing...`")
    result = await async_exec(cmd)
    await message.edit(f"**$** `{cmd}`\n\n**Output:**\n```bash\n{result}\n```")

@Client.on_message(filters.command("sys", prefixes=PREFIX) & filters.me)
async def system_stats(client, message: Message):
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    stats = (
        "**[ NEBULA SYSTEM STATS ]**\n\n"
        f"**CPU:** `{cpu}%`\n"
        f"**RAM:** `{mem.percent}%` (`{mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB`)\n"
        f"**Disk:** `{disk.percent}%`\n"
    )
    await message.edit(stats)

@Client.on_message(filters.command("update", prefixes=PREFIX) & filters.me)
async def update_bot(client, message: Message):
    """Memperbarui kode dari GitHub dan merestart bot."""
    await message.edit("`Checking for updates...`")
    out = await async_exec("git pull")
    
    if "Already up to date" in out:
        return await message.edit(f"✅ `{out}`")
    
    await message.edit(f"🔄 **Update Found:**\n`{out}`\n\n`Restarting Nebula...`")
    os._exit(0) # Docker/Termux (with script) will handle restart

@Client.on_message(filters.command("logs", prefixes=PREFIX) & filters.me)
async def view_logs(client, message: Message):
    """Melihat 20 baris terakhir dari log bot."""
    if not os.path.exists("nebula.log"):
        return await message.edit("`Log file tidak ditemukan.`")
        
    with open("nebula.log", "r") as f:
        lines = f.readlines()
        last_lines = "".join(lines[-20:])
        
    await message.edit(f"📜 **Nebula Logs (Last 20 lines):**\n\n```text\n{last_lines}```")

@Client.on_message(filters.command("ping", prefixes=PREFIX) & filters.me)
async def ping_pong(client, message: Message):
    start_time = time.time()
    await message.edit("`Pinging...`")
    end_time = time.time()
    latency = round((end_time - start_time) * 1000, 2)
    await message.edit(f"**Pong!**\nLatency: `{latency}ms`")
