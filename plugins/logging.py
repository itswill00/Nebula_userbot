from hydrogram import Client, filters
from hydrogram.types import Message


async def _log_guard_filter(_, client, message: Message):
    """Filter pintar untuk mencegah log spam dan feedback loop."""
    # 1. Selalu abaikan jika kejadian ada di dalam LOG_CHANNEL itu sendiri
    if message.chat and message.chat.id == client.log_channel:
        return False

    # 2. Ambil ID pengirim
    sender_id = message.from_user.id if message.from_user else None
    if not sender_id:
        return True

    # 3. Abaikan jika pengirim adalah saya (Userbot)
    if sender_id == client.me.id:
        return False

    # 4. Abaikan jika pengirim adalah Asisten Nebula
    if client.assistant and hasattr(client.assistant, "me") and client.assistant.me:
        if sender_id == client.assistant.me.id:
            return False

    return True


# Daftarkan filter kustom
log_guard = filters.create(_log_guard_filter)


@Client.on_message(log_guard, group=-1)
async def cache_messages(client, message: Message):
    """Mencatat setiap pesan masuk ke memori untuk Anti-Delete."""
    if not message.chat or not message.id:
        return

    chat_key = f"{message.chat.id}_{message.id}"
    client.db.msg_cache[chat_key] = {
        "text": message.text or message.caption or "[Media]",
        "from": message.from_user.first_name if message.from_user else "Seseorang",
        "chat": message.chat.title or "Private Chat"
    }

    if len(client.db.msg_cache) > 2000:
        oldest = next(iter(client.db.msg_cache))
        del client.db.msg_cache[oldest]


@Client.on_deleted_messages(group=-2)
async def on_deleted(client, messages):
    """Mendeteksi pesan yang dihapus dan mengirim laporan ke LOG_CHANNEL."""
    is_log_enabled = await client.db.get("anti_delete", True)
    if not is_log_enabled:
        return

    for msg in messages:
        if not msg or not hasattr(msg, "chat") or not msg.chat or not hasattr(msg, "id"):
            continue

        # Jangan log dari channel log sendiri
        if msg.chat.id == client.log_channel:
            continue

        chat_key = f"{msg.chat.id}_{msg.id}"
        if chat_key in client.db.msg_cache:
            cached = client.db.msg_cache[chat_key]
            log_text = (
                "🗑 **Message Deleted**\n"
                f"👤 **From:** `{cached['from']}`\n"
                f"📍 **Chat:** `{cached['chat']}`\n"
                f"📝 **Content:**\n`{cached['text']}`"
            )
            await client.send_log(log_text)
            del client.db.msg_cache[chat_key]


@Client.on_edited_message(log_guard, group=-3)
async def on_edited(client, message: Message):
    """Mendeteksi pesan yang diedit dan mengirim laporan ke LOG_CHANNEL."""
    is_log_enabled = await client.db.get("anti_edit", True)
    if not is_log_enabled:
        return

    if not message or not message.chat or not hasattr(message, "id"):
        return

    chat_key = f"{message.chat.id}_{message.id}"
    if chat_key in client.db.msg_cache:
        old_text = client.db.msg_cache[chat_key]['text']
        new_text = message.text or message.caption or "[Media]"

        if old_text != new_text:
            log_text = (
                "✏️ **Message Edited**\n"
                f"👤 **From:** `{message.from_user.first_name}`\n"
                f"📍 **Chat:** `{message.chat.title or 'Private'}`\n"
                f"❌ **Old:** `{old_text}`\n"
                f"✅ **New:** `{new_text}`"
            )
            await client.send_log(log_text)
            client.db.msg_cache[chat_key]['text'] = new_text
