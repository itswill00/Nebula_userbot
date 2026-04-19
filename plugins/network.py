import asyncio
import aiohttp
from hydrogram import Client, filters
from hydrogram.types import Message
from utils.shell import async_exec

PREFIX = "."

@Client.on_message(filters.command("speedtest", prefixes=PREFIX) & filters.me)
async def run_speedtest(client, message: Message):
    """Menjalankan pengujian jaringan VPS menggunakan Speedtest CLI."""
    status = await message.edit("`Menjalankan Speedtest... (Ini membutuhkan beberapa saat)`")
    try:
        # Kita menggunakan command shell speedtest-cli (dari package python)
        result = await async_exec("speedtest-cli --simple")
        await status.edit(f"**VPS Network Speed:**\n\n```bash\n{result}```")
    except Exception as e:
        await status.edit(f"**Speedtest Error:** `{str(e)}`")

@Client.on_message(filters.command("ip", prefixes=PREFIX) & filters.me)
async def track_ip(client, message: Message):
    """Mencari informasi IP atau lokasi server."""
    ip = "me"
    if len(message.command) > 1:
        ip = message.command[1]
    
    status = await message.edit("`Melacak IP...`")
    url = f"http://ip-api.com/json/{'' if ip == 'me' else ip}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            if data['status'] == 'success':
                info = (
                    f"🌐 **IP Information**\n\n"
                    f"**IP:** `{data['query']}`\n"
                    f"**Country:** `{data['country']}`\n"
                    f"**City:** `{data['city']}`\n"
                    f"**ISP:** `{data['isp']}`\n"
                    f"**Org:** `{data['org']}`"
                )
                await status.edit(info)
            else:
                await status.edit("`Gagal melacak IP.`")
