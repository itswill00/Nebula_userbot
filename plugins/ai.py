import os
import google.generativeai as genai
from hydrogram import Client, filters
from hydrogram.types import Message

# Inisialisasi Gemini
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

PREFIX = "."

@Client.on_message(filters.command("ask", prefixes=PREFIX) & filters.me)
async def ask_gemini(client, message: Message):
    """Tanya jawab dengan Gemini AI."""
    if not model:
        return await message.edit("`API Key Gemini belum diset di .env.`")
    
    if len(message.command) < 2:
        return await message.edit("`Masukkan pertanyaan.`")
    
    prompt = message.text.split(None, 1)[1]
    status = await message.edit("`Berpikir...`")
    
    try:
        response = model.generate_content(prompt)
        await status.edit(f"**Gemini AI:**\n\n{response.text}")
    except Exception as e:
        await status.edit(f"**AI Error:** `{str(e)}`")

@Client.on_message(filters.command("summarize", prefixes=PREFIX) & filters.me)
async def summarize_group(client, message: Message):
    """Merangkum 50 pesan terakhir di grup."""
    if not model:
        return await message.edit("`API Key Gemini belum diset di .env.`")
    
    status = await message.edit("`Membaca riwayat chat...`")
    
    messages = []
    async for msg in client.get_chat_history(message.chat.id, limit=50):
        if msg.text:
            user = msg.from_user.first_name if msg.from_user else "Unknown"
            messages.append(f"{user}: {msg.text}")
    
    if not messages:
        return await status.edit("`Tidak ada riwayat pesan teks yang bisa dirangkum.`")
    
    history_text = "\n".join(messages[::-1])
    prompt = f"Rangkum percakapan berikut secara singkat dan poin-poin penting:\n\n{history_text}"
    
    await status.edit("`Merangkum dengan AI...`")
    try:
        response = model.generate_content(prompt)
        await status.edit(f"**Ringkasan Percakapan:**\n\n{response.text}")
    except Exception as e:
        await status.edit(f"**AI Error:** `{str(e)}`")
