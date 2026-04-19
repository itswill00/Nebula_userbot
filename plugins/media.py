import os
import time
from hydrogram import Client, filters
from hydrogram.types import Message
from utils.media import video_to_sticker, ytdl_download

PREFIX = "."

@Client.on_message(filters.command("vstk", prefixes=PREFIX) & filters.me)
async def video_sticker_cmd(client, message: Message):
    """Mengubah video balasan menjadi Sticker Video Telegram."""
    replied = message.reply_to_message
    if not replied or not (replied.video or replied.document or replied.animation):
        return await message.edit("`Coba balas ke video atau GIF yang mau dijadiin sticker.`")

    status = await message.edit("`Sabar ya, lagi aku download videonya...`")
    input_path = await replied.download(file_name="downloads/")
    output_path = f"{input_path}.webm"
    
    await status.edit("`Lagi aku proses biar jadi sticker (WebM)...`")
    await video_to_sticker(input_path, output_path)
    
    if os.path.exists(output_path):
        await client.send_video_sticker(message.chat.id, output_path)
        await status.delete()
        os.remove(input_path)
        os.remove(output_path)
    else:
        await status.edit("`Waduh, maaf ya aku gagal ngolah videonya.`")

@Client.on_message(filters.command("dl", prefixes=PREFIX) & filters.me)
async def universal_downloader(client, message: Message):
    """Download video dari URL (YouTube, TikTok, IG, dll) ke Telegram."""
    if len(message.command) < 2:
        return await message.edit("`Berikan link URL.`")
    
    url = message.text.split(None, 1)[1]
    status = await message.edit(f"`Processing URL...`")
    
    try:
        start_time = time.time()
        file_path = await ytdl_download(url, "downloads/")
        duration = round(time.time() - start_time, 2)
        
        await status.edit(f"`Uploading... ({duration}s)`")
        await client.send_document(message.chat.id, file_path)
        await status.delete()
        os.remove(file_path)
    except Exception as e:
        await status.edit(f"**Error:** `{str(e)}`")
