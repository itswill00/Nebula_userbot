from core.client import NebulaBot
import uvloop
from hydrogram import filters
from hydrogram.handlers import MessageHandler, CallbackQueryHandler, InlineQueryHandler
from plugins.assistant import assistant_contact_handler, assistant_callback_handler
from plugins._inline import assistant_inline_handler, help_callback_handler, help_back_handler

if __name__ == "__main__":
    uvloop.install()
    bot = NebulaBot()
    
    # Konfigurasi Assistant Bot jika aktif
    if bot.assistant:
        bot.assistant.parent = bot
        
        # 1. Handler untuk Contact Bot (Pesan Masuk)
        bot.assistant.add_handler(
            MessageHandler(assistant_contact_handler, filters.private & ~filters.bot)
        )
        
        # 2. Handler untuk Callback Tombol
        bot.assistant.add_handler(
            CallbackQueryHandler(assistant_callback_handler)
        )
        bot.assistant.add_handler(
            CallbackQueryHandler(help_callback_handler, filters.regex(r"^help_"))
        )
        bot.assistant.add_handler(
            CallbackQueryHandler(help_back_handler, filters.regex("help_back"))
        )

        # 3. Handler untuk Inline Query
        bot.assistant.add_handler(
            InlineQueryHandler(assistant_inline_handler)
        )

    bot.run()
