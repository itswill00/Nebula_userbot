import asyncio
import yt_dlp
from hydrogram import Client
from hydrogram.types import Message
from core.decorators import on_cmd

@Client.on_message(on_cmd("yt", category="Media", info="Mencari video di YouTube."))
async def youtube_search(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "✦ Berikan kata kunci pencarian YouTube.")
    
    query = message.text.split(None, 1)[1]
    status = await client.fast_edit(message, f"⏳ `Mencari '{query}' di YouTube...`")
    
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'extract_flat': True,
        'quiet': True
    }
    
    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Cari 5 hasil teratas
            info = await loop.run_in_executor(
                None, 
                lambda: ydl.extract_info(f"ytsearch5:{query}", download=False)
            )
            
            if 'entries' in info and len(info['entries']) > 0:
                text = f"🔍 **Hasil Pencarian: `{query}`**\n\n"
                for i, entry in enumerate(info['entries']):
                    title = entry.get('title')
                    url = entry.get('url')
                    
                    # Format durasi
                    duration = entry.get('duration', 0)
                    mins = duration // 60 if duration else 0
                    secs = duration % 60 if duration else 0
                    duration_str = f"{mins}:{secs:02d}"
                    
                    text += f"**{i+1}.** [{title}]({url}) (`{duration_str}`)\n"
                
                await client.fast_edit(message, text, disable_web_page_preview=True)
            else:
                await client.fast_edit(message, "❌ **Tidak ada hasil yang ditemukan.**")
    except Exception as e:
        await client.fast_edit(message, f"❌ **Error Pencarian:** `{str(e)}`")
