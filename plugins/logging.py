from hydrogram import Client, filters
from hydrogram.types import Message

# Anti-Delete & Anti-Edit Engine
@Client.on_message(filters.all & ~filters.me, group=-1)
async def cache_messages(client, message: Message):
    """Cache every incoming message for logging purposes."""
    if not message.chat or not message.id:
        return
    
    # Store essential data in memory cache
    chat_key = f"{message.chat.id}_{message.id}"
    client.db.msg_cache[chat_key] = {
        "text": message.text or message.caption,
        "from": message.from_user.first_name if message.from_user else "Unknown",
        "chat": message.chat.title or "Private Chat"
    }
    
    # Keep cache small (max 2000 messages)
    if len(client.db.msg_cache) > 2000:
        oldest = next(iter(client.db.msg_cache))
        del client.db.msg_cache[oldest]

@Client.on_deleted_messages(group=-2)
async def on_deleted(client, messages):
    """Detect and log deleted messages."""
    is_log_enabled = await client.db.get("anti_delete", True)
    if not is_log_enabled:
        return

    for msg in messages:
        chat_key = f"{msg.chat.id}_{msg.id}"
        if chat_key in client.db.msg_cache:
            cached = client.db.msg_cache[chat_key]
            log_text = (
                "🗑 **Message Deleted**\n"
                f"👤 **From:** `{cached['from']}`\n"
                f"📍 **Chat:** `{cached['chat']}`\n"
                f"📝 **Content:**\n`{cached['text']}`"
            )
            await client.send_message("me", log_text)
            del client.db.msg_cache[chat_key]

@Client.on_edited_message(filters.all & ~filters.me, group=-3)
async def on_edited(client, message: Message):
    """Detect and log edited messages."""
    is_log_enabled = await client.db.get("anti_edit", True)
    if not is_log_enabled:
        return

    chat_key = f"{message.chat.id}_{message.id}"
    if chat_key in client.db.msg_cache:
        old_text = client.db.msg_cache[chat_key]['text']
        new_text = message.text or message.caption
        
        if old_text != new_text:
            log_text = (
                "✏️ **Message Edited**\n"
                f"👤 **From:** `{message.from_user.first_name}`\n"
                f"📍 **Chat:** `{message.chat.title or 'Private'}`\n"
                f"❌ **Old:** `{old_text}`\n"
                f"✅ **New:** `{new_text}`"
            )
            await client.send_message("me", log_text)
            # Update cache with new text
            client.db.msg_cache[chat_key]['text'] = new_text
