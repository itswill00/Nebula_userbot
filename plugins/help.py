from hydrogram import Client
from hydrogram.types import Message
from core.decorators import on_cmd


@Client.on_message(on_cmd("help", category="Config", info="Menampilkan menu bantuan modular bergaya Ultroid."))
async def help_menu(client, message: Message):
    """Memicu menu bantuan asisten."""
    if not client.assistant:
        return await client.fast_edit(message, "⚠️ **Kesalahan:** Bot Assistant tidak aktif.")

    try:
        # Kirim melalui asisten agar mendapatkan label 'via @bot'
        # Gunakan bot_username untuk pemicu inline
        bot_username = client.assistant.me.username
        results = await client.get_inline_bot_results(bot_username, "help")

        await client.send_inline_bot_result(
            chat_id=message.chat.id,
            query_id=results.query_id,
            result_id=results.results[0].id,
            reply_to_message_id=message.reply_to_message.id if message.reply_to_message else None
        )
        await message.delete()
    except Exception as e:
        # Fallback jika asisten tidak bisa kirim pesan
        await client.fast_edit(message, f"❌ **Gagal memicu Menu:**\n`{str(e)}`")
