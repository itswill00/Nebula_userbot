from hydrogram import Client, filters
from hydrogram.types import Message
from core.decorators import on_cmd
from plugins.assistant import get_help_markup

@Client.on_message(on_cmd("help", category="Config", info="Menampilkan menu bantuan interaktif (Pagination)."))
async def help_menu(client, message: Message):
    """Menampilkan menu bantuan gaya Ultroid dengan sistem geser halaman."""
    if not client.assistant:
        return await client.fast_edit(message, "⚠️ **Kesalahan:** Bot Assistant tidak aktif.")

    text = (
        "🌌 **Nebula Engine - Help Menu**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Pilih plugin di bawah ini untuk melihat detail perintah dan pengaturan.\n"
        "Gunakan tombol `«` dan `»` untuk beralih halaman."
    )
    
    markup = await get_help_markup(page=0)
    
    try:
        await client.assistant.send_message(
            message.chat.id, 
            text, 
            reply_markup=markup
        )
        await message.delete()
    except Exception as e:
        await client.fast_edit(message, f"❌ **Gagal mengirim Menu:**\n`{str(e)}`")
