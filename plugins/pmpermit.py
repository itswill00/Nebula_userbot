from hydrogram import Client, filters, enums
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from core.decorators import on_cmd, brain_rule
from core.brain import Action, Intent

# Default batas peringatan
MAX_WARNS = 3


@brain_rule
async def pm_permit_rule(client, ctx):
    if not ctx["pm_permit"]:
        return None

    message = ctx["message"]
    chat_id = message.chat.id
    user_id = ctx["user_id"]

    is_private = (
        ctx["chat_type"] == enums.ChatType.PRIVATE or
        str(ctx["chat_type"]) == "ChatType.PRIVATE"
    )

    if not is_private:
        return None

    # Abaikan bot, pesan servis, atau pesan kosong
    if not message.from_user or message.from_user.is_bot or getattr(message, "service", False):
        return None

    approved_list = ctx["pm_approved"]

    # Lewati jika sudah disetujui atau diri sendiri
    if user_id in approved_list or user_id == client.me.id:
        return None

    # Auto-approve Kontak
    if message.from_user.is_contact:
        approved_list.append(user_id)
        await client.db.set("pm_approved", list(set(approved_list)))
        return None

    # Ambil data peringatan dari DB
    pm_warns = await client.db.get("pm_warns", {})
    user_warn_data = pm_warns.get(
        str(user_id), {"count": 0, "last_msg_id": None})

    warns = user_warn_data["count"] + 1
    user_warn_data["count"] = warns

    # Blokir Otomatis jika melebihi batas
    if warns >= MAX_WARNS:
        async def execute_block():
            await message.reply(
                "🚫 **Batas peringatan tercapai.**\n"
                "Anda telah diblokir otomatis karena terus mengirim pesan tanpa persetujuan."
            )
            await client.block_user(user_id)

            # Notifikasi ke Log Channel
            log_msg = (
                f"👤 #Blocked\n"
                f"**User:** {message.from_user.mention} [`{user_id}`]\n"
                f"**Alasan:** Spamming tanpa izin (Warns: {warns}/{MAX_WARNS})"
            )
            await client.send_log(log_msg)

            # Cleanup DB
            if str(user_id) in pm_warns:
                del pm_warns[str(user_id)]
            await client.db.set("pm_warns", pm_warns)

        return Action(intent=Intent.BLOCK, plugin_name="pmpermit", execute=execute_block)

    # Kirim Peringatan
    text = (
        f"🛡️ **Nebula Security - PM Permit**\n\n"
        f"Halo, {message.from_user.mention}! Saya asisten keamanan.\n"
        f"Mohon maaf, Bos saya sedang sibuk dan tidak menerima PM dari orang baru.\n\n"
        f"⚠️ **Peringatan:** `{warns}/{MAX_WARNS}`\n"
        f"Jangan mengirim pesan berulang atau Anda akan **diblokir otomatis**."
    )

    async def execute_warn():
        # Cleanup: Hapus peringatan sebelumnya
        last_msg_id = user_warn_data.get("last_msg_id")
        if last_msg_id:
            try:
                await client.delete_messages(chat_id, last_msg_id)
            except Exception:
                pass

        # Balas dengan tombol Minta Izin jika asisten aktif
        if client.assistant:
            buttons = [[InlineKeyboardButton(
                "📩 Minta Izin", callback_data=f"pm_request_{user_id}")]]
            rep = await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            rep = await message.reply(text)

        # Update DB dengan ID pesan terbaru
        user_warn_data["last_msg_id"] = rep.id
        pm_warns[str(user_id)] = user_warn_data
        await client.db.set("pm_warns", pm_warns)

    return Action(intent=Intent.REPLY_BLOCK, plugin_name="pmpermit", execute=execute_warn)


@Client.on_message(filters.me & filters.outgoing & filters.private, group=2)
async def auto_approve_pm(client, message: Message):
    """Otomatis menyetujui user jika kita mengirim pesan duluan."""
    if message.text and message.text.startswith((".", "/")):
        return

    user_id = message.chat.id
    if not user_id:
        return

    approved_list = await client.db.get("pm_approved", [])
    if user_id not in approved_list:
        approved_list.append(user_id)
        await client.db.set("pm_approved", approved_list)

        # Cleanup data peringatan jika ada
        pm_warns = await client.db.get("pm_warns", {})
        if str(user_id) in pm_warns:
            del pm_warns[str(user_id)]
            await client.db.set("pm_warns", pm_warns)

        await client.send_log(
            f"👤 #AutoApproved\n"
            f"**User:** `{user_id}`\n"
            f"**Alasan:** Outgoing message dikirim."
        )


@Client.on_message(on_cmd("pmpermit", category="Security", info="Aktifkan/Matikan fitur PM Permit."))
async def toggle_pm(client, message: Message):
    current = await client.db.get("pm_permit_enabled", True)
    new_state = not current
    await client.db.set("pm_permit_enabled", new_state)
    status = "AKTIF" if new_state else "NON-AKTIF"
    await client.fast_edit(message, f"🛡️ **PM Permit sekarang:** `{status}`")


@Client.on_message(on_cmd(["approve", "a"], category="Security", info="Setujui seseorang untuk PM."))
async def approve_pm(client, message: Message):
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try:
            user_id = int(message.command[1])
        except ValueError:
            return await client.fast_edit(message, "⚠️ **Kesalahan:** `ID User harus berupa angka.`")
    elif message.chat.type == enums.ChatType.PRIVATE:
        user_id = message.chat.id

    if not user_id:
        return await client.fast_edit(message, "⚠️ **Kesalahan:** `Balas pesan atau berikan ID user.`")

    approved_list = await client.db.get("pm_approved", [])
    if user_id not in approved_list:
        approved_list.append(user_id)
        await client.db.set("pm_approved", approved_list)

        # Cleanup peringatan
        pm_warns = await client.db.get("pm_warns", {})
        if str(user_id) in pm_warns:
            data = pm_warns.pop(str(user_id))
            if data.get("last_msg_id"):
                try:
                    await client.delete_messages(user_id, data["last_msg_id"])
                except Exception:
                    pass
            await client.db.set("pm_warns", pm_warns)

        await client.fast_edit(message, f"✅ **User** `{user_id}` **telah disetujui.**")
        await client.send_log(f"👤 #Approved\n**User:** `{user_id}`\n**Oleh:** Anda")
    else:
        await client.fast_edit(message, f"ℹ️ **User** `{user_id}` **sudah ada di daftar putih.**")


@Client.on_message(on_cmd(["disapprove", "da"], category="Security", info="Hapus persetujuan PM seseorang."))
async def disapprove_pm(client, message: Message):
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try:
            user_id = int(message.command[1])
        except ValueError:
            return await client.fast_edit(message, "⚠️ **Kesalahan:** `ID User harus berupa angka.`")
    elif message.chat.type == enums.ChatType.PRIVATE:
        user_id = message.chat.id

    if not user_id:
        return await client.fast_edit(message, "⚠️ **Kesalahan:** `Balas pesan atau berikan ID user.`")

    approved_list = await client.db.get("pm_approved", [])
    if user_id in approved_list:
        approved_list.remove(user_id)
        await client.db.set("pm_approved", approved_list)
        await client.fast_edit(message, f"❌ **Persetujuan untuk user** `{user_id}` **telah dicabut.**")
        await client.send_log(f"👤 #Disapproved\n**User:** `{user_id}`\n**Oleh:** Anda")
    else:
        await client.fast_edit(message, f"ℹ️ **User** `{user_id}` **memang belum disetujui.**")
