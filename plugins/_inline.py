from hydrogram import Client, filters
from hydrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

COLUMNS = 2

def get_main_help_menu(registry):
    """Fungsi pembantu untuk menyusun menu utama secara dinamis."""
    categories = sorted(registry.keys())
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
    return buttons

async def assistant_inline_handler(client, inline_query: InlineQuery):
    """Menangani permintaan menu bantuan via @bot_username help."""
    if inline_query.query.lower() != "help":
        return

    registry = client.parent.cmd_help
    help_text = (
        "🌌 **Nebula — Control Center**\n\n"
        f"Hello **{inline_query.from_user.first_name}**! "
        "I am your digital assistant. Please select a category below to explore my capabilities."
    )
    
    results = [
        InlineQueryResultArticle(
            id="help_menu",
            title="Nebula Interactive Help",
            input_message_content=InputTextMessageContent(help_text),
            reply_markup=InlineKeyboardMarkup(get_main_help_menu(registry))
        )
    ]
    await inline_query.answer(results, cache_time=1)

@Client.on_callback_query(filters.regex(r"^help_"))
async def help_callback_handler(client, callback_query: CallbackQuery):
    """Dispatcher responsif untuk interaksi tombol bantuan."""
    data = callback_query.data
    user_me = await client.parent.get_me()
    
    if callback_query.from_user.id != user_me.id:
        return await callback_query.answer("⚠️ Not Authorized.", show_alert=True)
    
    await callback_query.answer()

    if data == "help_back":
        registry = client.parent.cmd_help
        help_text = "🌌 **Nebula — Control Center**\n\nSelect a category to see available commands."
        await callback_query.edit_message_text(
            help_text, 
            reply_markup=InlineKeyboardMarkup(get_main_help_menu(registry))
        )
        return

    if data.startswith("help_mod_"):
        category = data.split("_")[2]
        
        # Dashboard Interaktif untuk Modul Config
        if category == "Config":
            text = await client.parent.get_string("DASHBOARD_TEXT")
            is_ad = await client.parent.db.get("anti_delete", True)
            is_as = await client.parent.db.get("antispam", False)
            lang = await client.parent.db.get("lang", "id")
            
            buttons = [
                [
                    InlineKeyboardButton(f"Anti-Delete: {'✅' if is_ad else '❌'}", callback_data="conf_anti_delete"),
                    InlineKeyboardButton(f"Anti-Spam: {'✅' if is_as else '❌'}", callback_data="conf_antispam")
                ],
                [
                    InlineKeyboardButton(f"Bahasa: {lang.upper()}", callback_data="conf_lang_switch")
                ],
                [
                    InlineKeyboardButton("⬅️ Back to Menu", callback_data="help_back")
                ]
            ]
            return await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

        if category == "Stats":
            import psutil
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            text = f"📊 **Nebula Operational Stats**\n\n**CPU:** `{cpu}%`\n**RAM:** `{mem}%`"
        else:
            cmds = client.parent.cmd_help.get(category, {})
            text = f"📂 **Module: {category}**\n\n"
            for cmd, info in cmds.items():
                text += f"• `.{cmd}` - {info}\n"
            if not cmds:
                text += "_No commands registered in this module._"

        buttons = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="help_back")]]
        await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
