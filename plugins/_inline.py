from hydrogram import Client, filters
from hydrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

async def assistant_inline_handler(client, inline_query: InlineQuery):
    """Menangani permintaan menu bantuan via @bot_username help."""
    query = inline_query.query.lower()
    
    if query == "help":
        help_text = "🌌 **Nebula — Pusat Kendali Kamu**\n\nHalo! Mau aku bantu apa hari ini? Pilih kategori di bawah ya."
        
        # Ambil kategori secara dinamis dari registry parent (Userbot)
        categories = sorted(client.parent.cmd_help.keys())
        buttons = []
        
        # Susun tombol 2 kolom secara dinamis
        for i in range(0, len(categories), 2):
            row = [InlineKeyboardButton(categories[i], callback_data=f"help_{categories[i]}")]
            if i + 1 < len(categories):
                row.append(InlineKeyboardButton(categories[i+1], callback_data=f"help_{categories[i+1]}"))
            buttons.append(row)
        
        # Tambah tombol Dashboard di bawah
        buttons.append([InlineKeyboardButton("⚙️ Setelan", callback_data="help_Config")])
        
        results = [
            InlineQueryResultArticle(
                id="help_menu",
                title="Nebula Help Menu",
                description="Pusat kontrol interaktif Nebula",
                input_message_content=InputTextMessageContent(help_text),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        ]
        await inline_query.answer(results, cache_time=1)

@Client.on_callback_query(filters.regex(r"^help_"))
async def help_callback_handler(client, callback_query: CallbackQuery):
    """Menampilkan detail perintah dari kategori yang dipilih."""
    category = callback_query.data.split("_")[1]
    
    if category == "back":
        # Logika kembali ke menu utama
        help_text = "🌌 **Nebula — Pusat Kendali Kamu**\n\nHalo! Mau aku bantu apa hari ini? Pilih kategori di bawah ya."
        categories = sorted(client.parent.cmd_help.keys())
        buttons = []
        for i in range(0, len(categories), 2):
            row = [InlineKeyboardButton(categories[i], callback_data=f"help_{categories[i]}")]
            if i + 1 < len(categories):
                row.append(InlineKeyboardButton(categories[i+1], callback_data=f"help_{categories[i+1]}"))
            buttons.append(row)
        buttons.append([InlineKeyboardButton("⚙️ Setelan", callback_data="help_Config")])
        return await callback_query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup(buttons))

    # Ambil daftar perintah dari registry
    cmds = client.parent.cmd_help.get(category, {})
    text = f"✨ **Modul {category}**\n\n"
    
    for cmd, info in cmds.items():
        text += f"• `.{cmd}` - {info}\n"
    
    if not cmds:
        text += "Belum ada perintah di modul ini."

    buttons = [[InlineKeyboardButton("⬅️ Kembali", callback_data="help_back")]]
    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
