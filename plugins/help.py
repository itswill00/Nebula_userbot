from hydrogram import Client, filters
from hydrogram.types import Message
from core.decorators import on_cmd
from plugins.assistant import get_main_menu_markup

@Client.on_message(on_cmd("help", category="Config", info="Menampilkan menu bantuan interaktif modular."))
async def help_menu(client, message: Message):
    """Menampilkan menu bantuan gaya Ultroid/Userge (Modular + Paginated)."""
    if not client.assistant:
        return await client.fast_edit(message, "⚠️ **Kesalahan:** Bot Assistant tidak aktif.")

    text = (
        "🌌 **Nebula Engine - Help Menu**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Jelajahi plugin berdasarkan kategori di bawah ini.\n"
        "Setiap plugin memiliki halaman bantuan dan kontrolnya sendiri."
    )
    
    markup = await get_main_menu_markup()
    
    try:
        # Userbot memicu asisten untuk mengirim menu via inline
        # Catatan: Kita gunakan send_message via asisten ke chat yang sama
        # (Aman karena asisten biasanya ada di grup atau PM)
        await client.assistant.send_message(
            message.chat.id, 
            text, 
            reply_markup=markup
        )
        await message.delete()
    except Exception as e:
        # Fallback jika asisten tidak bisa kirim pesan (misal: bukan admin di grup)
        # Gunakan inline query (seperti yang kita pelajari dari Ultroid)
        try:
            bot_username = client.assistant.me.username
            results = await client.get_inline_bot_results(bot_username, "help")
            await client.send_inline_bot_result(
                chat_id=message.chat.id,
                query_id=results.query_id,
                result_id=results.results[0].id
            )
            await message.delete()
        except:
            await client.fast_edit(message, f"❌ **Gagal:** Asisten tidak dapat merespons di chat ini.")
