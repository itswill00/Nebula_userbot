import warnings
import uvloop
from hydrogram import filters
from hydrogram.handlers import MessageHandler, CallbackQueryHandler, InlineQueryHandler

from core.client import NebulaBot
from plugins.assistant import assistant_contact_handler, assistant_callback_handler
from plugins._inline import assistant_inline_handler

# Bungkam peringatan versi Python dari Google agar terminal bersih
warnings.filterwarnings("ignore", category=FutureWarning, module="google.api_core")

if __name__ == "__main__":
    uvloop.install()
    bot = NebulaBot()

    # Konfigurasi Assistant Bot jika aktif
    if bot.assistant:
        bot.assistant.parent = bot

        # 1. Pesan Masuk (Contact Bot)
        bot.assistant.add_handler(
            MessageHandler(assistant_contact_handler, filters.private & ~filters.bot)
        )

        # 2. SEMUA Callback (Help, Dashboard, Toggles, Navigasi)
        bot.assistant.add_handler(
            CallbackQueryHandler(
                assistant_callback_handler,
                filters.regex(r"^(cat_|all_|pdet_|utog_|back_|close_|info_)")
            )
        )

        # 3. Inline Query (@bot help)
        bot.assistant.add_handler(
            InlineQueryHandler(assistant_inline_handler)
        )

    print("✨ \033[96mNebula Ready! Memulai sistem...\033[0m")
    bot.run()
