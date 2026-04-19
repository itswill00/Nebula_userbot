from hydrogram import Client, filters
from hydrogram.types import Message

PREFIX = "."

@Client.on_message(filters.command("help", prefixes=PREFIX) & filters.me)
async def help_menu(client, message: Message):
    """Dynamic help menu listing all available commands."""
    help_text = (
        "🌌 **Nebula Userbot God Mode**\n\n"
        "**System & Network:**\n"
        "`.sh <cmd>` - Exec shell\n"
        "`.eval <code>` - Exec Python\n"
        "`.sys` - VPS Stats\n"
        "`.speedtest` - Test Network\n"
        "`.ip [ip]` - Lookup IP Info\n\n"
        "**Media & Download:**\n"
        "`.vstk` - Video to Sticker\n"
        "`.dl <url>` - YTDL Universal\n"
        "`.leech <url>` - Aria2 Leech\n\n"
        "**Intelligence & Utility:**\n"
        "`.ask <q>` - Gemini AI\n"
        "`.summarize` - Chat summary\n"
        "`.tr <lang>` - Translate (AI)\n"
        "`.tts <text>` - Text to Speech\n"
        "`.weather <city>` - Live Weather\n\n"
        "**Admin & Security:**\n"
        "`.approve` - Allow PM\n"
        "`.purge` - Bulk delete\n"
        "`.ban/kick/mute` - Moderation"
    )
    await message.edit(help_text)
