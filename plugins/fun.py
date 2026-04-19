import asyncio
from hydrogram import Client
from hydrogram.types import Message
from core.decorators import on_cmd

@Client.on_message(on_cmd("hack", category="Fun", info="Animasi terminal hacking (Prank)."))
async def hack_animation(client, message: Message):
    target = message.text.split(None, 1)[1] if len(message.command) > 1 else "Unknown"
    
    stages = [
        f"⏳ `Connecting to {target}'s device...`",
        f"⏳ `Bypassing security protocols...`",
        f"⏳ `Extracting Telegram session...`",
        f"⏳ `Downloading private galleries...`",
        f"⏳ `Uploading data to dark web...`",
        f"✅ **Hacking Complete!**\n\nTarget: `{target}`\nStatus: `Pwned`"
    ]
    
    for stage in stages:
        await client.fast_edit(message, stage)
        await asyncio.sleep(1.5)

@Client.on_message(on_cmd("type", category="Fun", info="Animasi mengetik pesan satu per satu."))
async def type_animation(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "✦ Berikan teks yang ingin diketik.")
    
    text = message.text.split(None, 1)[1]
    typed_text = ""
    
    for char in text:
        typed_text += char
        # Tambah kursor agar terlihat nyata
        await client.fast_edit(message, f"`{typed_text}█`")
        await asyncio.sleep(0.1)
        
    # Hapus kursor di akhir
    await client.fast_edit(message, f"`{text}`")
