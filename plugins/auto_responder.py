from hydrogram import Client, filters
from hydrogram.types import Message

PREFIX = "."

@Client.on_message(filters.command("addresp", prefixes=PREFIX) & filters.me)
async def add_auto_response(client, message: Message):
    """Menambah respon otomatis. Format: .addresp <keyword>|<response>"""
    if "|" not in message.text:
        return await message.edit("`Format: .addresp <keyword>|<response>`")
    
    parts = message.text.split(None, 1)[1].split("|", 1)
    keyword = parts[0].strip().lower()
    response = parts[1].strip()
    
    responses = await client.db.get("auto_responses", {})
    responses[keyword] = response
    await client.db.set("auto_responses", responses)
    
    await message.edit(f"✅ `Respon otomatis ditambahkan untuk keyword:` `{keyword}`")

@Client.on_message(filters.command("delresp", prefixes=PREFIX) & filters.me)
async def del_auto_response(client, message: Message):
    """Menghapus respon otomatis."""
    if len(message.command) < 2:
        return await message.edit("`Berikan keyword yang ingin dihapus.`")
    
    keyword = message.command[1].lower()
    responses = await client.db.get("auto_responses", {})
    
    if keyword in responses:
        del responses[keyword]
        await client.db.set("auto_responses", responses)
        await message.edit(f"✅ `Respon untuk keyword {keyword} dihapus.`")
    else:
        await message.edit("`Keyword tidak ditemukan.`")

@Client.on_message(filters.all & ~filters.me, group=1)
async def trigger_auto_response(client, message: Message):
    """Mendeteksi keyword dan membalas secara otomatis."""
    if not message.text:
        return
        
    responses = await client.db.get("auto_responses", {})
    text = message.text.lower()
    
    for keyword, response in responses.items():
        if keyword in text:
            await message.reply(response)
            break
