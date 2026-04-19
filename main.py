from core.client import NebulaBot
import uvloop
from hydrogram import filters
from hydrogram.handlers import MessageHandler, CallbackQueryHandler, InlineQueryHandler
from plugins.assistant import assistant_contact_handler, assistant_callback_handler
from plugins._inline import assistant_inline_handler, help_callback_handler

if __name__ == "__main__":
    uvloop.install()
    bot = NebulaBot()
    
    # Konfigurasi Assistant Bot jika aktif
    if bot.assistant:
        bot.assistant.parent = bot
        
        # 1. Handler untuk Contact Bot (Pesan Masuk dari orang asing)
        bot.assistant.add_handler(
            MessageHandler(assistant_contact_handler, filters.private & ~filters.bot)
        )
        
        # 2. Handler untuk Callback Dashboard (Setting Bot)
        bot.assistant.add_handler(
            CallbackQueryHandler(assistant_callback_handler, filters.regex(r"^conf_|^close_db$"))
        )
        
        # 3. Handler untuk Callback Menu Bantuan (.help)
        bot.assistant.add_handler(
            CallbackQueryHandler(help_callback_handler, filters.regex(r"^help_"))
        )

        # 4. Handler untuk Inline Query (@bot_username help)
        bot.assistant.add_handler(
            InlineQueryHandler(assistant_inline_handler)
        )

    bot.run()
