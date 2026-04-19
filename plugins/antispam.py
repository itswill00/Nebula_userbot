from hydrogram import Client, filters
from hydrogram.types import Message, ChatPermissions

from core.decorators import brain_rule
from core.brain import Action, Intent

# Dictionary in-memory untuk melacak aktivitas (user_id: [timestamps])
SPAM_TRACKER = {}
# Konfigurasi: 5 pesan dalam 8 detik dianggap spam
MSG_LIMIT = 5
TIME_WINDOW = 8


@brain_rule
async def antispam_rule(client, ctx):
    if not ctx["antispam"]:
        return None

    message = ctx["message"]
    chat_type = ctx["chat_type"]
    chat_type_val = chat_type.value if hasattr(
        chat_type, "value") else str(chat_type)

    if chat_type_val not in ("group", "supergroup", "ChatType.GROUP", "ChatType.SUPERGROUP"):
        return None

    if not message.from_user or message.from_user.is_bot or getattr(message, "service", False) or getattr(message, "empty", False):
        return None

    user_id = ctx["user_id"]
    current_time = ctx["time"]

    if user_id not in SPAM_TRACKER:
        SPAM_TRACKER[user_id] = []

    # Tambah timestamp pesan baru
    SPAM_TRACKER[user_id].append(current_time)

    # Bersihkan timestamps yang sudah di luar jendela waktu
    SPAM_TRACKER[user_id] = [t for t in SPAM_TRACKER[user_id]
                             if current_time - t < TIME_WINDOW]

    if len(SPAM_TRACKER[user_id]) > MSG_LIMIT:
        async def execute_mute():
            try:
                # Mute user selama 1 jam
                await client.restrict_chat_member(
                    message.chat.id,
                    user_id,
                    ChatPermissions(can_send_messages=False),
                    until_date=int(current_time + 3600)
                )
                await message.reply(f"🔇 **Spam Detected!**\nUser `{user_id}` telah di-mute selama 1 jam.")
                # Hapus histori agar tidak terpicu lagi segera
                SPAM_TRACKER[user_id] = []
            except Exception:
                pass  # Bot mungkin tidak punya akses admin

        return Action(intent=Intent.MUTE, plugin_name="antispam", execute=execute_mute)

    return None


@Client.on_message(filters.command("antispam", prefixes=".") & filters.me)
async def toggle_antispam(client, message: Message):
    """Mengaktifkan atau menonaktifkan fitur anti-spam."""
    if len(message.command) < 2:
        return await message.edit("`Gunakan .antispam on/off`")

    state = message.command[1].lower() == "on"
    await client.db.set("antispam", state)
    await message.edit(f"🛡 **Anti-Spam Engine:** `{'ON' if state else 'OFF'}`")
