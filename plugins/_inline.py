from hydrogram import Client, filters
from hydrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import math

# Konfigurasi Pagination
COLUMNS = 2
ROWS = 4

async def assistant_inline_handler(client, inline_query: InlineQuery):
    """Menangani permintaan menu bantuan via @bot_username help."""
    query = inline_query.query.lower()
    
    if query == "help":
        # Mengambil data dari registry global
        registry = client.parent.cmd_help
        categories = sorted(registry.keys())
        
        help_text = (
            "🌌 **Nebula — Control Center**\n\n"
            f"Hello **{inline_query.from_user.first_name}**! "
            "I am your digital assistant. Please select a category below to explore my capabilities."
        )
        
        buttons = []
        for i in range(0, len(categories), COLUMNS):
            row = [
                InlineKeyboardButton(
                    f"📁 {categories[j]}", 
                    callback_data=f"help_mod_{categories[j]}"
                ) for j in range(i, min(i + COLUMNS, len(categories)))
            ]
            buttons.append(row)
        
        # Tombol Navigasi Bawah
        buttons.append([
            InlineKeyboardButton("⚙️ Settings", callback_data="help_mod_Config"),
            InlineKeyboardButton("📊 Stats", callback_data="help_mod_Stats")
        ])
        
        results = [
            InlineQueryResultArticle(
                id="help_menu",
                title="Nebula Interactive Help",
                description="Browse all available modules and commands",
                input_message_content=InputTextMessageContent(help_text),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        ]
        await inline_query.answer(results, cache_time=1)

@Client.on_callback_query(filters.regex(r"^help_"))
async def help_callback_handler(client, callback_query: CallbackQuery):
    """Main Dispatcher untuk seluruh interaksi tombol bantuan."""
    data = callback_query.data
    user_me = await client.parent.get_me()
    
    # Keamanan: Hanya pemilik bot yang bisa menekan tombol
    if callback_query.from_user.id != user_me.id:
        return await callback_query.answer("⚠️ Not Authorized. This is a private userbot.", show_alert=True)

    if data == "help_back":
        # Kembali ke Menu Utama
        categories = sorted(client.parent.cmd_help.keys())
        buttons = []
        for i in range(0, len(categories), COLUMNS):
            row = [
                InlineKeyboardButton(
                    f"📁 {categories[j]}", 
                    callback_data=f"help_mod_{categories[j]}"
                ) for j in range(i, min(i + COLUMNS, len(categories)))
            ]
            buttons.append(row)
        buttons.append([
            InlineKeyboardButton("⚙️ Settings", callback_data="help_mod_Config"),
            InlineKeyboardButton("📊 Stats", callback_data="help_mod_Stats")
        ])
        
        help_text = "🌌 **Nebula — Control Center**\n\nSelect a category to see available commands."
        await callback_query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup(buttons))
        return

    if data.startswith("help_mod_"):
        # Menampilkan isi modul tertentu
        category = data.split("_")[2]
        
        # Logika khusus untuk Stats
        if category == "Stats":
            import psutil
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            text = f"📊 **Nebula Operational Stats**\n\n**Uptime:** `Active`\n**CPU:** `{cpu}%`\n**RAM:** `{mem}%`"
        else:
            cmds = client.parent.cmd_help.get(category, {})
            text = f"📂 **Module: {category}**\n\n"
            for cmd, info in cmds.items():
                text += f"• `.{cmd}` - {info}\n"
            if not cmds:
                text += "_No commands registered in this module._"

        buttons = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="help_back")]]
        await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        await callback_query.answer()
