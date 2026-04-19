import time
import psutil
from hydrogram import Client, filters
from hydrogram.types import Message
from utils.shell import async_exec

PREFIX = "."

@Client.on_message(filters.command("sh", prefixes=PREFIX) & filters.me)
async def shell_runner(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("`Berikan perintah shell.`")
        
    cmd = message.text.split(maxsplit=1)[1]
    await message.edit_text("`Executing...`")
    
    result = await async_exec(cmd)
    
    response = f"**$** `{cmd}`\n\n**Output:**\n```bash\n{result}\n```"
    await message.edit_text(response)


@Client.on_message(filters.command("sys", prefixes=PREFIX) & filters.me)
async def system_stats(client: Client, message: Message):
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    stats = (
        "**[ NEBULA SYSTEM STATS ]**\n\n"
        f"**CPU:** `{cpu}%`\n"
        f"**RAM:** `{mem.percent}%` (`{mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB`)\n"
        f"**Disk:** `{disk.percent}%` (`{disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB`)\n"
    )
    await message.edit_text(stats)


@Client.on_message(filters.command("ping", prefixes=PREFIX) & filters.me)
async def ping_pong(client: Client, message: Message):
    start_time = time.time()
    await message.edit_text("`Pinging...`")
    end_time = time.time()
    
    latency = round((end_time - start_time) * 1000, 2)
    await message.edit_text(f"**Pong!**\nLatency: `{latency}ms`")
