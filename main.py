from core.client import NebulaBot
import uvloop
from hydrogram import filters
from hydrogram.handlers import MessageHandler, CallbackQueryHandler
from plugins.assistant import assistant_contact_handler, assistant_callback_handler

if __name__ == "__main__":
    uvloop.install()
    bot = NebulaBot()
    
    # Hubungkan Assistant jika aktif
    if bot.assistant:
        # Tambahkan referensi parent untuk akses DB dari Assistant
        bot.assistant.parent = bot
        
        # Handler untuk Contact Bot (Assistant menerima PM dari orang lain)
        bot.assistant.add_handler(
            MessageHandler(assistant_contact_handler, filters.private & ~filters.bot)
        )
        
        # Handler untuk Dashboard (Callback Tombol)
        bot.assistant.add_handler(
            CallbackQueryHandler(assistant_callback_handler)
        )

    bot.run()
