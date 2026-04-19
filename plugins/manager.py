import os
import aiohttp
import importlib
from hydrogram import Client, filters
from hydrogram.types import Message

PREFIX = "."

@Client.on_message(filters.command("load", prefixes=PREFIX) & filters.me)
async def load_plugin_cmd(client, message: Message):
    """Memuat plugin yang ada di folder plugins."""
    if len(message.command) < 2:
        return await message.edit("`Berikan nama plugin.`")
    
    name = message.command[1]
    await message.edit(f"`Loading {name}...`")
    
    try:
        importlib.import_module(f"plugins.{name}")
        await message.edit(f"✅ `Plugin {name} loaded.`")
    except Exception as e:
        await message.edit(f"❌ `Error:`\n`{str(e)}`")

@Client.on_message(filters.command("reload", prefixes=PREFIX) & filters.me)
async def reload_plugin_cmd(client, message: Message):
    """Me-reload plugin yang sudah ada di memori."""
    if len(message.command) < 2:
        return await message.edit("`Berikan nama plugin.`")
    
    name = message.command[1]
    await message.edit(f"`Reloading {name}...`")
    
    if await client.reload_plugin(name):
        await message.edit(f"✅ `Plugin {name} reloaded.`")
    else:
        await message.edit(f"❌ `Gagal me-reload {name}.`")

@Client.on_message(filters.command("install", prefixes=PREFIX) & filters.me)
async def install_plugin_cmd(client, message: Message):
    """Instal plugin langsung dari URL."""
    if len(message.command) < 2:
        return await message.edit("`Berikan URL file plugin (.py).`")
    
    url = message.text.split(None, 1)[1]
    name = url.split("/")[-1]
    
    if not name.endswith(".py"):
        return await message.edit("`URL harus mengarah ke file .py.`")

    status = await message.edit(f"`Installing {name}...`")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    content = await resp.read()
                    file_path = f"plugins/{name}"
                    with open(file_path, "wb") as f:
                        f.write(content)
                    
                    # Load plugin setelah di-save
                    plugin_name = name.replace(".py", "")
                    importlib.import_module(f"plugins.{plugin_name}")
                    await status.edit(f"✅ `Plugin {name} installed and loaded.`")
                else:
                    await status.edit(f"❌ `Download failed: HTTP {resp.status}`")
    except Exception as e:
        await status.edit(f"❌ `Installation error:`\n`{str(e)}`")
