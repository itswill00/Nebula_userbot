from hydrogram import Client, filters
from hydrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Definisi Pengelompokan Modul
CORE_MODULES = ["System", "Media", "Admin"]
UTILITY_MODULES = ["Scraper", "Intelligence", "Identity", "Fun"]

def get_main_help_menu():
    """Menyusun menu utama bantuan yang ringkas."""
    buttons = [
        [
            InlineKeyboardButton("🚀 System", callback_data="help_mod_System"),
            InlineKeyboardButton("🎬 Media", callback_data="help_mod_Media")
        ],
        [
            InlineKeyboardButton("🛡 Admin", callback_data="help_mod_Admin"),
            InlineKeyboardButton("🛠 Utilitas", callback_data="help_sub_utility")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="help_mod_Config"),
            InlineKeyboardButton("📊 Stats", callback_data="help_mod_Stats")
        ]
    ]
    return buttons

def get_utility_menu():
    """Menyusun sub-menu untuk kategori utilitas."""
    buttons = [
        [
            InlineKeyboardButton("🔍 Scraper", callback_data="help_mod_Scraper"),
            InlineKeyboardButton("🧠 AI Tools", callback_data="help_mod_Intelligence")
        ],
        [
            InlineKeyboardButton("👤 Identity", callback_data="help_mod_Identity"),
            InlineKeyboardButton("🎈 Fun", callback_data="help_mod_Fun")
        ],
        [
            InlineKeyboardButton("⬅️ Kembali", callback_data="help_back")
        ]
    ]
    return buttons

async def assistant_inline_handler(client, inline_query: InlineQuery):
    """Menangani permintaan menu bantuan via @bot_username help."""
    if inline_query.query.lower() != "help":
        return

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
            reply_markup=InlineKeyboardMarkup(get_main_help_menu())
        )
    ]
    await inline_query.answer(results, cache_time=1)

@Client.on_callback_query(filters.regex(r"^help_"))
async def help_callback_handler(client, callback_query: CallbackQuery):
    """Dispatcher untuk navigasi menu bantuan."""
    data = callback_query.data
    user_me = await client.parent.get_me()
    
    if callback_query.from_user.id != user_me.id:
        return await callback_query.answer("⚠️ Not Authorized.", show_alert=True)
    
    await callback_query.answer()

    # Navigasi Kembali ke Menu Utama
    if data == "help_back":
        help_text = "🌌 **Nebula — Control Center**\n\nSelect a category to see available commands."
        return await callback_query.edit_message_text(
            help_text, 
            reply_markup=InlineKeyboardMarkup(get_main_help_menu())
        )

    # Membuka Sub-Menu Utilitas
    if data == "help_sub_utility":
        text = "🛠 **Module: Utilitas**\n\nPilih kategori utilitas di bawah untuk melihat detail perintah."
        return await callback_query.edit_message_text(
            text, 
            reply_markup=InlineKeyboardMarkup(get_utility_menu())
        )

    # Menangani Detail Modul
    if data.startswith("help_mod_"):
        category = data.split("_")[2]
        back_target = "help_back"
        
        # Tentukan tombol kembali (jika dari utility, kembali ke utility menu)
        if category in UTILITY_MODULES:
            back_target = "help_sub_utility"
        
        # Logika khusus Config
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
                [InlineKeyboardButton("⬅️ Kembali", callback_data="help_back")]
            ]
            return await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

        # Logika khusus Stats
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

        buttons = [[InlineKeyboardButton("⬅️ Kembali", callback_data=back_target)]]
        await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
