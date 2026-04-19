import os
from hydrogram import Client, filters
from hydrogram.types import Message
from utils.graphics import convert_to_sticker

PREFIX = "."


@Client.on_message(filters.command("kang", prefixes=PREFIX) & filters.me)
async def kang_sticker(client, message: Message):
    """Mencuri sticker atau gambar untuk diubah menjadi file PNG (dasar untuk pack pribadi)."""
    replied = message.reply_to_message
    if not replied or not (replied.sticker or replied.photo):
        return await message.edit("`Balas ke sticker atau foto.`")

    status = await message.edit("`Kanging...`")
    input_path = await replied.download(file_name="downloads/")
    output_path = f"{input_path}.png"

    try:
        convert_to_sticker(input_path, output_path)
        await client.send_document(
            message.chat.id,
            output_path,
            caption="`Kanged! (PNG Format)`"
        )
        await status.delete()
        os.remove(input_path)
        os.remove(output_path)
    except Exception as e:
        await status.edit(f"❌ `Kang Error:`\n`{str(e)}`")


@Client.on_message(filters.command("getsticker", prefixes=PREFIX) & filters.me)
async def extract_sticker(client, message: Message):
    """Mengambil file mentah dari sticker (PNG/WebM)."""
    replied = message.reply_to_message
    if not replied or not replied.sticker:
        return await message.edit("`Balas ke sticker.`")

    status = await message.edit("`Extracting...`")
    file_path = await replied.download(file_name="downloads/")
    await client.send_document(message.chat.id, file_path, caption="`Raw Sticker File.`")
    await status.delete()
    os.remove(file_path)


@Client.on_message(filters.command("quotly", prefixes=PREFIX) & filters.me)
async def create_quote(client, message: Message):
    """Membuat quote estetik dari pesan teks menggunakan Gemini AI (Vision)."""
    replied = message.reply_to_message
    if not replied or not replied.text:
        return await message.edit("`Balas ke pesan teks.`")

    await message.edit("`Rendering Quote...`")
    # Versi Sederhana: Karena Quotly membutuhkan API eksternal, kita gunakan teks berformat
    quote_text = (
        f"“{replied.text}”\n\n"
        f"— {replied.from_user.first_name if replied.from_user else 'Unknown'}"
    )
    # Di masa depan, ini bisa diintegrasikan dengan canvas/pil untuk rendering gambar.
    await message.edit(f"**Nebula Quotes:**\n\n`{quote_text}`")
