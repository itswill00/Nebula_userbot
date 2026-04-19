import os
import aiohttp
from gtts import gTTS
from hydrogram import Client, filters
from hydrogram.types import Message
import google.generativeai as genai
from plugins.ai import model

PREFIX = "."

@Client.on_message(filters.command("tts", prefixes=PREFIX) & filters.me)
async def text_to_speech(client, message: Message):
    """Konversi teks ke Voice Note (suara)."""
    text = ""
    lang = "id"
    
    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
        if len(message.command) > 1:
            lang = message.command[1]
    elif len(message.command) > 1:
        text = message.text.split(maxsplit=1)[1]
    else:
        return await message.edit("`Berikan teks atau balas pesan.`")

    status = await message.edit("`Speaking...`")
    
    try:
        tts = gTTS(text, lang=lang)
        tts.save("downloads/tts.ogg")
        await client.send_voice(message.chat.id, "downloads/tts.ogg", reply_to_message_id=message.id)
        await status.delete()
        os.remove("downloads/tts.ogg")
    except Exception as e:
        await status.edit(f"**TTS Error:** `{str(e)}`")

@Client.on_message(filters.command("tr", prefixes=PREFIX) & filters.me)
async def translate_text(client, message: Message):
    """Penerjemah menggunakan Gemini 1.5 Flash (Sangat Akurat)."""
    if not model:
        return await message.edit("`API Key Gemini belum diset.`")

    lang = "id"
    text = ""
    if len(message.command) > 1:
        lang = message.command[1]
        
    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
    elif len(message.command) > 2:
        text = message.text.split(maxsplit=2)[2]
    else:
        return await message.edit("`Balas pesan atau ketik teks. Format: .tr <lang> <text>`")

    prompt = f"Terjemahkan teks berikut ke bahasa {lang}. Hanya berikan hasil terjemahannya saja tanpa penjelasan lain:\n\n{text}"
    status = await message.edit("`Translating...`")
    
    try:
        response = model.generate_content(prompt)
        await status.edit(f"**Terjemahan ({lang}):**\n\n`{response.text.strip()}`")
    except Exception as e:
        await status.edit(f"**Tr Error:** `{str(e)}`")

@Client.on_message(filters.command("weather", prefixes=PREFIX) & filters.me)
async def get_weather(client, message: Message):
    """Mengambil informasi cuaca menggunakan wttr.in secara asinkronus."""
    if len(message.command) < 2:
        return await message.edit("`Masukkan nama kota.`")
    
    city = message.text.split(maxsplit=1)[1]
    status = await message.edit(f"`Mencari cuaca di {city}...`")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://wttr.in/{city}?format=%C+%t|%w|%h") as resp:
            if resp.status == 200:
                data = (await resp.text()).strip().split("|")
                if len(data) == 3:
                    text = f"⛅ **Cuaca di {city.title()}:**\n\n**Suhu:** `{data[0]}`\n**Angin:** `{data[1]}`\n**Kelembapan:** `{data[2]}`"
                    return await status.edit(text)
    
    await status.edit("`Gagal mengambil data cuaca.`")
