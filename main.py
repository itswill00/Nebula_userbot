import warnings
# Bungkam peringatan versi Python dari Google agar terminal tetap bersih
warnings.filterwarnings("ignore", category=FutureWarning, module="google.api_core")

import uvloop
from hydrogram import filters
from hydrogram.handlers import MessageHandler, CallbackQueryHandler, InlineQueryHandler

from core.client import NebulaBot
from plugins.assistant import assistant_contact_handler, assistant_callback_handler
from plugins._inline import assistant_inline_handler, help_callback_handler

if __name__ == "__main__":
    uvloop.install()
    bot = NebulaBot()
    
    # Konfigurasi Assistant Bot jika aktif
    if bot.assistant:
        bot.assistant.parent = bot
        
        # Handler Assistant
        bot.assistant.add_handler(MessageHandler(assistant_contact_handler, filters.private & ~filters.bot))
        bot.assistant.add_handler(CallbackQueryHandler(assistant_callback_handler, filters.regex(r"^conf_|^close_db$")))
        bot.assistant.add_handler(CallbackQueryHandler(help_callback_handler, filters.regex(r"^help_")))
        bot.assistant.add_handler(InlineQueryHandler(assistant_inline_handler))

    print("✨ \033[96mNebula Ready! Memulai sistem...\033[0m")
    bot.run()
