from hydrogram import Client, filters
from hydrogram.types import Message
from core.decorators import on_cmd

@Client.on_message(on_cmd("help", category="Config", info="Menampilkan menu bantuan interaktif."))
async def help_menu(client, message: Message):
    """Menampilkan menu bantuan via Inline Query (Ultroid Style)."""
    
    # 1. Cek keberadaan asisten
    if not client.assistant:
        return await client.fast_edit(message, "⚠️ **Kesalahan:** Bot Assistant tidak aktif.")

    # 2. Cek apakah asisten sudah terkoneksi/start (Mencegah ConnectionError)
    if not getattr(client.assistant, "me", None):
        try:
            # Jika belum ada cache me, coba ambil dengan timeout pendek
            bot_info = await client.assistant.get_me()
            bot_username = bot_info.username
        except Exception:
            return await client.fast_edit(message, "⏳ **Menghubungkan...** Asisten sedang bersiap, coba lagi sebentar.")
    else:
        bot_username = client.assistant.me.username

    try:
        # Picu inline query ke bot sendiri
        results = await client.get_inline_bot_results(bot_username, "help")
        
        if not results or not results.results:
            return await client.fast_edit(message, "❌ **Gagal:** Menu bantuan tidak ditemukan di asisten.")

        # Kirim hasil pertama dari query tersebut
        await client.send_inline_bot_result(
            chat_id=message.chat.id,
            query_id=results.query_id,
            result_id=results.results[0].id,
            reply_to_message_id=message.reply_to_message.id if message.reply_to_message else None
        )
        
        # Hapus pesan perintah (.help)
        await message.delete()
        
    except Exception as e:
        await client.fast_edit(message, f"❌ **Gagal memicu Inline Menu:**\n`{str(e)}`")
