from hydrogram import Client, filters
from hydrogram.types import Message

PREFIX = "."

@Client.on_message(filters.command("help", prefixes=PREFIX) & filters.me)
async def help_menu(client, message: Message):
    """Dynamic help menu listing all available commands."""
    # This bot uses a modular approach, help is curated manually for cleaner output
    help_text = (
        "🌌 **Nebula Userbot Help Menu**\n\n"
        "**System Tools:**\n"
        "`.sh <cmd>` - Execute shell\n"
        "`.sys` - VPS Stats\n"
        "`.ping` - Latency test\n\n"
        "**Media & Download:**\n"
        "`.vstk` - Video to Sticker\n"
        "`.dl <url>` - Universal Downloader\n"
        "`.leech <url>` - High-speed Leech (Aria2)\n\n"
        "**Security & AI:**\n"
        "`.approve` - Approve PM\n"
        "`.ask <q>` - Gemini AI\n"
        "`.summarize` - Summarize Chat\n\n"
        "**Admin & Tools:**\n"
        "`.purge` - Bulk delete\n"
        "`.save/get` - Local JSON DB\n"
        "`.ban/kick/mute` - Admin action"
    )
    await message.edit(help_text)
