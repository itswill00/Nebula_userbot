from hydrogram import Client
from hydrogram.types import Message
from core.decorators import on_cmd


@Client.on_message(on_cmd("setvar", category="Config", info="Setel variabel konfigurasi bot secara global."))
async def set_var(client, message: Message):
    if len(message.command) < 3:
        return await client.fast_edit(message, "⚠️ **Format Salah!**\nGunakan: `.setvar <nama_key> <nilai>`")

    key = message.command[1].lower()
    value = message.text.split(None, 2)[2]

    # Konversi otomatis untuk tipe data umum
    if value.lower() in ["true", "yes", "on"]:
        value = True
    elif value.lower() in ["false", "no", "off"]:
        value = False
    elif value.isdigit():
        value = int(value)

    await client.db.set(key, value)
    await client.fast_edit(message, f"✅ **Variabel Diperbarui!**\n`{key}` ➔ `{value}`")


@Client.on_message(on_cmd("getvar", category="Config", info="Ambil nilai variabel dari database."))
async def get_var(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "⚠️ **Format Salah!**\nGunakan: `.getvar <nama_key>`")

    key = message.command[1].lower()
    value = await client.db.get(key)

    if value is None:
        return await client.fast_edit(message, f"❌ **Variabel `{key}` tidak ditemukan.**")

    await client.fast_edit(message, f"🔍 **Detail Variabel:**\n`{key}` ➔ `{value}`")


@Client.on_message(on_cmd("delvar", category="Config", info="Hapus variabel dari database."))
async def del_var(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "⚠️ **Format Salah!**\nGunakan: `.delvar <nama_key>`")

    key = message.command[1].lower()
    deleted = await client.db.delete(key)

    if deleted:
        await client.fast_edit(message, f"✅ **Variabel `{key}` berhasil dihapus.**")
    else:
        await client.fast_edit(message, f"❌ **Variabel `{key}` tidak ditemukan.**")


@Client.on_message(on_cmd(["vars", "setting"], category="Config", info="Lihat semua konfigurasi aktif."))
async def list_vars(client, message: Message):
    all_data = await client.db.all_data()
    if not all_data:
        return await client.fast_edit(message, "📭 **Database masih kosong.**")

    text = "⚙️ **Nebula Config Manager**\n\n"
    for key, val in all_data.items():
        # Sembunyikan data sensitif jika ada (misal session)
        if "session" in key.lower() or "token" in key.lower():
            val = "********"
        text += f"• `{key}`: `{val}`\n"

    text += "\n_Gunakan `.setvar <key> <val>` untuk mengubah._"
    
    if len(text) > 4096:
        # Jika terlalu panjang, kirim sebagai log atau potong
        text = text[:4000] + "..."
    
    await client.fast_edit(message, text)
