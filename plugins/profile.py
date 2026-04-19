import os
from hydrogram import Client, filters
from hydrogram.types import Message
from core.decorators import on_cmd

@Client.on_message(on_cmd("setname", category="Identity", info="Ubah nama depan & belakang (contoh: .setname John | Doe)"))
async def set_name(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "✦ Berikan nama. Format: `.setname Depan | Belakang`")
    
    parts = message.text.split(None, 1)[1].split("|", 1)
    first_name = parts[0].strip()
    last_name = parts[1].strip() if len(parts) > 1 else ""
    
    await client.update_profile(first_name=first_name, last_name=last_name)
    await client.fast_edit(message, f"✅ **Identitas Diperbarui**\n\n**Nama:** `{first_name} {last_name}`")

@Client.on_message(on_cmd("setbio", category="Identity", info="Ubah bio profil Telegram kamu."))
async def set_bio(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "✦ Berikan teks bio.")
    
    bio = message.text.split(None, 1)[1]
    await client.update_profile(bio=bio)
    await client.fast_edit(message, f"✅ **Bio Diperbarui**\n\n`{bio}`")

@Client.on_message(on_cmd("clone", category="Identity", info="Salin nama dan foto profil user lain."))
async def clone_profile(client, message: Message):
    replied = message.reply_to_message
    if not replied or not replied.from_user:
        return await client.fast_edit(message, "✦ Balas ke pesan target yang ingin di-clone.")
    
    await client.fast_edit(message, "⏳ `Menganalisis profil target...`")
    target = replied.from_user
    
    # Clone Nama
    await client.update_profile(first_name=target.first_name, last_name=target.last_name or "")
    
    # Clone PFP
    photos = []
    async for photo in client.get_chat_photos(target.id, limit=1):
        photos.append(photo)
    
    if photos:
        await client.fast_edit(message, "⏳ `Mengambil foto profil target...`")
        photo_path = await client.download_media(photos[0].file_id)
        await client.set_profile_photo(photo=photo_path)
        os.remove(photo_path)
        
    await client.fast_edit(message, f"✅ **Kloning Selesai**\n\nBerhasil menjadi klon dari `{target.first_name}`.")

@Client.on_message(on_cmd("block", category="Identity", info="Blokir pengguna."))
async def block_user(client, message: Message):
    replied = message.reply_to_message
    if not replied or not replied.from_user:
        return await client.fast_edit(message, "✦ Balas ke user yang ingin diblokir.")
    
    user = replied.from_user
    await client.block_user(user.id)
    await client.fast_edit(message, f"🚫 **Diblokir**\n\nUser `{user.first_name}` ({user.id}) telah diblokir.")
