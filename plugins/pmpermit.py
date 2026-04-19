import asyncio
from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from core.decorators import on_cmd, brain_rule
from core.brain import Action, Intent

# In-memory cache untuk menghitung peringatan (user_id: count)
PM_WARNS = {}
MAX_WARNS = 3

@brain_rule
async def pm_permit_rule(client, ctx):
    if not ctx["pm_permit"]:
        return None

    message = ctx["message"]
    chat_type = ctx["chat_type"]
    chat_type_val = chat_type.value if hasattr(chat_type, "value") else str(chat_type)
    
    if chat_type_val != "private" and chat_type_val != "ChatType.PRIVATE":
        return None
        
    if not message.from_user or message.from_user.is_bot or getattr(message, "service", False) or getattr(message, "empty", False):
        return None

    user_id = ctx["user_id"]
    approved_list = ctx["pm_approved"]
    
    if user_id in approved_list or user_id == client.me.id:
        return None

    if message.from_user.is_contact:
        approved_list.append(user_id)
        await client.db.set("pm_approved", list(set(approved_list)))
        return None

    warns = PM_WARNS.get(user_id, 0) + 1
    PM_WARNS[user_id] = warns

    if warns >= MAX_WARNS:
        async def execute_block():
            await message.reply("🚫 **Batas peringatan tercapai.** Anda telah diblokir karena terus mengirim pesan tanpa persetujuan.")
            await client.block_user(user_id)
            if user_id in PM_WARNS:
                del PM_WARNS[user_id]
        return Action(intent=Intent.BLOCK, plugin_name="pmpermit", execute=execute_block)

    text = (
        f"🇮🇩 **Halo! Saya adalah sistem keamanan Nebula.**\n\n"
        f"Bos saya sedang tidak menerima PM dari orang asing. "
        f"Silakan tunggu hingga beliau menyetujui pesan Anda.\n\n"
        f"⚠️ **Peringatan:** `{warns}/{MAX_WARNS}`\n"
        f"Jangan spam atau Anda akan diblokir otomatis!"
    )
    
    async def execute_warn():
        if client.assistant:
            buttons = [[InlineKeyboardButton("📩 Minta Izin", callback_data=f"pm_request_{user_id}")]]
            await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await message.reply(text)

    return Action(intent=Intent.REPLY_BLOCK, plugin_name="pmpermit", execute=execute_warn)

@Client.on_message(on_cmd("pmpermit", category="Security", info="Aktifkan/Matikan fitur PM Permit."))
async def toggle_pm(client, message: Message):
    current = await client.db.get("pm_permit_enabled", True)
    new_state = not current
    await client.db.set("pm_permit_enabled", new_state)
    status = "AKTIF" if new_state else "NON-AKTIF"
    await client.fast_edit(message, f"🛡️ **PM Permit sekarang:** `{status}`")

@Client.on_message(on_cmd("approve", category="Security", info="Setujui seseorang untuk PM."))
async def approve_pm(client, message: Message):
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        user_id = int(message.command[1])
    elif message.chat.type == "private":
        user_id = message.chat.id
    
    if not user_id:
        return await client.fast_edit(message, "⚠️ **Kesalahan:** `Balas pesan atau berikan ID user.`")

    approved_list = await client.db.get("pm_approved", [])
    if user_id not in approved_list:
        approved_list.append(user_id)
        await client.db.set("pm_approved", approved_list)
        if user_id in PM_WARNS:
            del PM_WARNS[user_id]
        await client.fast_edit(message, f"✅ **User** `{user_id}` **telah disetujui.**")
    else:
        await client.fast_edit(message, f"ℹ️ **User** `{user_id}` **sudah ada di daftar putih.**")

@Client.on_message(on_cmd("disapprove", category="Security", info="Hapus persetujuan PM seseorang."))
async def disapprove_pm(client, message: Message):
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        user_id = int(message.command[1])
    elif message.chat.type == "private":
        user_id = message.chat.id

    if not user_id:
        return await client.fast_edit(message, "⚠️ **Kesalahan:** `Balas pesan atau berikan ID user.`")

    approved_list = await client.db.get("pm_approved", [])
    if user_id in approved_list:
        approved_list.remove(user_id)
        await client.db.set("pm_approved", approved_list)
        await client.fast_edit(message, f"❌ **Persetujuan untuk user** `{user_id}` **telah dicabut.**")
    else:
        await client.fast_edit(message, f"ℹ️ **User** `{user_id}` **memang belum disetujui.**")
