from hydrogram import Client, filters
from hydrogram.types import Message
from core.decorators import on_cmd

@Client.on_message(on_cmd("help", category="Config", info="Menampilkan menu bantuan interaktif via Inline."))
async def help_menu(client, message: Message):
    """Menampilkan menu bantuan gaya Ultroid via Inline Query."""
    if not client.assistant:
        return await client.fast_edit(message, "⚠️ **Kesalahan:** Bot Assistant tidak aktif.")

    # Gunakan cache username asisten
    bot_username = client.assistant.me.username

    try:
        # Userbot melakukan inline query ke Assistant Bot
        results = await client.get_inline_bot_results(bot_username, "help")
        
        if not results or not results.results:
            return await client.fast_edit(message, "❌ **Gagal:** Asisten tidak merespons query bantuan.")

        # Kirim hasil inline ke chat (Akun Anda yang mengirim, jadi aman dari USER_IS_BOT)
        await client.send_inline_bot_result(
            chat_id=message.chat.id,
            query_id=results.query_id,
            result_id=results.results[0].id,
            reply_to_message_id=message.reply_to_message.id if message.reply_to_message else None
        )
        
        await message.delete()
        
    except Exception as e:
        await client.fast_edit(message, f"❌ **Gagal memicu Inline Menu:**\n`{str(e)}`")
