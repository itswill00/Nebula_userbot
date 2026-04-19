import os
import aiohttp
import json
from gtts import gTTS
from hydrogram import Client, filters
from hydrogram.types import Message
from core.decorators import on_cmd

@Client.on_message(on_cmd("tts", category="Tools", info="Konversi teks ke Voice Note."))
async def text_to_speech(client, message: Message):
    text = ""
    lang = "id"
    
    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
        if len(message.command) > 1:
            lang = message.command[1]
    elif len(message.command) > 1:
        text = message.text.split(maxsplit=1)[1]
    else:
        return await client.fast_edit(message, "⚠️ **Kesalahan:** `Berikan teks atau balas pesan.`")

    status = await client.fast_edit(message, "🎙️ **Memproses TTS...**")
    
    try:
        tts = gTTS(text, lang=lang)
        dest = "downloads/tts.ogg"
        tts.save(dest)
        await client.send_voice(message.chat.id, dest, reply_to_message_id=message.id)
        await status.delete()
        if os.path.exists(dest):
            os.remove(dest)
    except Exception as e:
        await client.fast_edit(status, f"❌ **TTS Error:** `{str(e)}`")

@Client.on_message(on_cmd("json", category="Tools", info="Dapatkan encoding JSON pesan."))
async def get_json(client, message: Message):
    reply = message.reply_to_message
    if not reply:
        return await client.fast_edit(message, "⚠️ **Kesalahan:** `Balas ke sebuah pesan.`")
    
    data = str(reply)
    if len(data) > 4000:
        with open("message.json", "w") as f:
            f.write(data)
        await client.send_document(message.chat.id, "message.json", caption="📄 **JSON Output**")
        os.remove("message.json")
    else:
        await client.fast_edit(message, f"📄 **JSON Output:**\n\n```json\n{data}\n```")

@Client.on_message(on_cmd("calc", category="Tools", info="Kalkulator matematika sederhana."))
async def calculator(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "⚠️ **Kesalahan:** `Masukkan ekspresi matematika.`")
    
    expr = message.text.split(maxsplit=1)[1]
    try:
        # Gunakan eval yang aman (hanya angka dan operator dasar)
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in expr):
            raise ValueError("Karakter tidak diizinkan.")
        
        result = eval(expr)
        await client.fast_edit(message, f"🔢 **Kalkulator**\n\n**Input:** `{expr}`\n**Hasil:** `{result}`")
    except Exception as e:
        await client.fast_edit(message, f"❌ **Error:** `{str(e)}`")

@Client.on_message(on_cmd("ipinfo", category="Tools", info="Dapatkan informasi alamat IP."))
async def ip_info(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "⚠️ **Kesalahan:** `Masukkan alamat IP.`")
    
    ip = message.command[1]
    status = await client.fast_edit(message, f"🔍 **Mencari info IP {ip}...**")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://ip-api.com/json/{ip}") as resp:
            data = await resp.json()
            if data.get("status") == "success":
                res = (
                    f"🌐 **IP Information**\n\n"
                    f"**IP:** `{data.get('query')}`\n"
                    f"**Country:** `{data.get('country')} ({data.get('countryCode')})`\n"
                    f"**Region:** `{data.get('regionName')}`\n"
                    f"**City:** `{data.get('city')}`\n"
                    f"**ISP:** `{data.get('isp')}`\n"
                    f"**ASN:** `{data.get('as')}`"
                )
                await client.fast_edit(status, res)
            else:
                await client.fast_edit(status, "❌ **Gagal mendapatkan info IP.**")

@Client.on_message(on_cmd("shorten", category="Tools", info="Pendekkan URL menggunakan TinyURL."))
async def shorten_url(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "⚠️ **Kesalahan:** `Masukkan URL.`")
    
    url = message.command[1]
    status = await client.fast_edit(message, "🔗 **Memendekkan URL...**")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://tinyurl.com/api-create.php?url={url}") as resp:
            if resp.status == 200:
                short_url = await resp.text()
                await client.fast_edit(status, f"🔗 **Shortened URL:**\n\n`{short_url}`")
            else:
                await client.fast_edit(status, "❌ **Gagal memendekkan URL.**")
