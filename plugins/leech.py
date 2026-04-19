import os
import asyncio
from hydrogram import Client, filters
from hydrogram.types import Message
from utils.aria2 import Aria2RPC

PREFIX = "."
aria2 = Aria2RPC()

@Client.on_message(filters.command("leech", prefixes=PREFIX) & filters.me)
async def leech_cmd(client, message: Message):
    """Download file dari link ke VPS dan unggah ke Telegram."""
    if len(message.command) < 2:
        return await message.edit("`Berikan link URL.`")
    
    url = message.text.split(None, 1)[1]
    status = await message.edit("`Aria2: Adding to queue...`")
    
    try:
        gid = await aria2.add_url(url)
        await status.edit(f"`Downloading... GID: {gid}`")
        
        # Polling status unduhan
        while True:
            info = await aria2.get_status(gid)
            if info['status'] == 'complete':
                break
            elif info['status'] == 'error':
                return await status.edit(f"`Download Error: {info['errorMessage']}`")
            
            # Update progres (sederhana)
            total = int(info['totalLength'])
            completed = int(info['completedLength'])
            progress = round((completed / total) * 100, 2) if total > 0 else 0
            await status.edit(f"`Downloading: {progress}%`")
            await asyncio.sleep(3)
        
        file_path = info['files'][0]['path']
        await status.edit("`Uploading to Telegram...`")
        await client.send_document(message.chat.id, file_path)
        await status.delete()
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        await status.edit(f"**Leech Error:** `{str(e)}`")
