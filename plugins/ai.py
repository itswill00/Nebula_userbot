import os
import google.generativeai as genai
from hydrogram import Client, filters
from hydrogram.types import Message
from core.decorators import on_cmd

# Inisialisasi Gemini
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

@Client.on_message(on_cmd("ask", category="Intelligence", info="Tanya jawab cerdas dengan Gemini AI."))
async def ask_gemini(client, message: Message):
    if not model:
        return await message.edit("`Waduh, API Key Gemini kamu belum dipasang.`")
    if len(message.command) < 2:
        return await message.edit("`Mau tanya apa? Ketik pertanyaannya ya.`")
    
    prompt = message.text.split(None, 1)[1]
    status = await message.edit("`Bentar ya, aku mikir dulu...`")
    try:
        response = model.generate_content(prompt)
        await status.edit(f"💡 **Hasil Pemikiran:**\n\n{response.text}")
    except Exception as e:
        await status.edit(f"😓 **Error pas mikir:** `{str(e)}`")

@Client.on_message(on_cmd("summarize", category="Intelligence", info="Rangkum obrolan grup yang panjang."))
async def summarize_group(client, message: Message):
    if not model:
        return await message.edit("`API Key Gemini belum ada nih.`")
    status = await message.edit("`Sabar ya, aku baca riwayat chatnya dulu...`")
    
    messages = []
    async for msg in client.get_chat_history(message.chat.id, limit=50):
        if msg.text:
            user = msg.from_user.first_name if msg.from_user else "Seseorang"
            messages.append(f"{user}: {msg.text}")
    
    if not messages:
        return await status.edit("`Grup sepi, nggak ada yang bisa dirangkum.`")
    
    history_text = "\n".join(messages[::-1])
    prompt = f"Summarize this conversation like a professional assistant reporting to their boss:\n\n{history_text}"
    
    await status.edit("`Lagi aku buatin ringkasannya...`")
    try:
        response = model.generate_content(prompt)
        await status.edit(f"📝 **Ringkasan Buat Kamu:**\n\n{response.text}")
    except Exception as e:
        await status.edit(f"❌ **Gagal ngerangkum:** `{str(e)}`")
