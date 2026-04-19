from hydrogram import Client, filters
from hydrogram.types import Message

PREFIX = "."

@Client.on_message(filters.command("help", prefixes=PREFIX) & filters.me)
async def help_menu(client, message: Message):
    """Menampilkan menu bantuan via Inline Query (Ultroid Style)."""
    
    if not client.assistant:
        return await message.edit("`Bot Assistant tidak aktif.`")

    # Ambil username bot assistant
    bot_info = await client.assistant.get_me()
    bot_username = bot_info.username

    try:
        # Picu inline query ke bot sendiri
        # Ini memungkinkan pengiriman tombol tanpa bot harus ada di grup
        results = await client.get_inline_bot_results(bot_username, "help")
        
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
        await message.edit(f"❌ **Gagal memicu Inline Menu:**\n`{str(e)}`")
