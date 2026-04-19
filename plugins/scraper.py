import aiohttp
import wikipedia
from hydrogram import Client
from hydrogram.types import Message
from core.decorators import on_cmd

# Setting bahasa wikipedia
wikipedia.set_lang("id")


@Client.on_message(on_cmd("wiki", category="Scraper", info="Cari artikel di Wikipedia."))
async def search_wiki(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "✦ Ketik judul artikel yang dicari.")

    query = message.text.split(None, 1)[1]
    await client.fast_edit(message, f"⏳ `Mencari '{query}' di Wikipedia...`")

    try:
        # Batasi rangkuman max 3 kalimat
        result = wikipedia.summary(query, sentences=3)
        page = wikipedia.page(query)

        text = f"📖 **Wikipedia: {page.title}**\n\n`{result}`\n\n🔗 [Baca Selengkapnya]({page.url})"
        await client.fast_edit(message, text, disable_web_page_preview=True)
    except wikipedia.exceptions.DisambiguationError as e:
        await client.fast_edit(message, f"❌ Topik terlalu umum. Coba spesifik. Opsi:\n`{e.options[:5]}`")
    except Exception as e:
        await client.fast_edit(message, f"❌ **Gagal:** `{str(e)}`")


@Client.on_message(on_cmd("github", category="Scraper", info="Ambil profil pengguna GitHub."))
async def github_user(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "✦ Masukkan username GitHub.")

    user = message.text.split(None, 1)[1]
    await client.fast_edit(message, "⏳ `Menghubungkan ke GitHub...`")

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.github.com/users/{user}") as resp:
            if resp.status == 200:
                data = await resp.json()

                info = (
                    f"🐙 **GitHub Profile: {data.get('name') or user}**\n\n"
                    f"👤 **Username:** `{data.get('login')}`\n"
                    f"🏢 **Company:** `{data.get('company') or '-'}`\n"
                    f"📍 **Lokasi:** `{data.get('location') or '-'}`\n"
                    f"📚 **Public Repos:** `{data.get('public_repos')}`\n"
                    f"👥 **Followers:** `{data.get('followers')}` | **Following:** `{data.get('following')}`\n"
                    f"📝 **Bio:** `{data.get('bio') or '-'}`\n\n"
                    f"🔗 [Lihat Profil]({data.get('html_url')})"
                )
                await client.fast_edit(message, info, disable_web_page_preview=True)
            else:
                await client.fast_edit(message, f"❌ **User `{user}` tidak ditemukan.**")
