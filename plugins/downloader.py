import os
import time
import asyncio
import yt_dlp
from hydrogram import Client, filters
from hydrogram.types import Message
from core.decorators import on_cmd

# Lokasi penyimpanan sementara
DOWNLOAD_DIR = "downloads/"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def progress_bar(current, total, status_msg, start_time):
    """Fungsi pembantu untuk menampilkan progress bar."""
    now = time.time()
    diff = now - start_time
    if diff < 1:
        return
    
    percentage = current * 100 / total
    speed = current / diff
    elapsed_time = round(diff) * 1000
    time_to_completion = round((total - current) / speed) * 1000
    
    # Visual Progress Bar
    pro_bar = ""
    for i in range(10):
        if percentage >= (i + 1) * 10:
            pro_bar += "■"
        else:
            pro_bar += "□"

    progress_str = (
        f"📥 **Downloading...**\n\n"
        f"📊 **Progress:** `{pro_bar} {round(percentage, 2)}%`\n"
        f"🚀 **Speed:** `{round(speed / 1024 / 1024, 2)} MB/s`\n"
        f"📦 **Size:** `{round(total / 1024 / 1024, 2)} MB`\n"
        f"⏳ **ETA:** `{round(time_to_completion / 1000)}s`"
    )
    return progress_str

@Client.on_message(on_cmd("dl", category="Download", info="Download media dari YouTube, TikTok, dll."))
async def universal_downloader(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "⚠️ **Kesalahan:** `Berikan link video.`")

    url = message.command[1]
    status = await client.fast_edit(message, "🔍 **Menganalisis link...**")
    
    # Opsi yt-dlp
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': f'{DOWNLOAD_DIR}%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'video')
            
            await status.edit(f"📥 **Mendownload:**\n`{title}`")
            
            # Proses Download Sebenarnya
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: ydl.download([url]))

        # Kirim ke Telegram
        if os.path.exists(filename):
            await status.edit("📤 **Mengirim ke Telegram...**")
            start_time = time.time()
            
            await client.send_video(
                chat_id=message.chat.id,
                video=filename,
                caption=f"✅ **Downloaded:** `{title}`\n🔗 **Source:** [Link]({url})",
                progress=lambda c, t: client.loop.create_task(
                    status.edit(progress_bar(c, t, "Uploading", start_time))
                ) if c % (1024 * 1024) == 0 else None
            )
            
            await status.delete()
            os.remove(filename)
        else:
            await status.edit("❌ **Gagal:** `File tidak ditemukan setelah download.`")

    except Exception as e:
        await status.edit(f"❌ **Error:** `{str(e)}`")

@Client.on_message(on_cmd("song", category="Download", info="Download audio/lagu dari YouTube/Spotify link."))
async def song_downloader(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "⚠️ **Kesalahan:** `Berikan link atau judul lagu.`")

    query = message.text.split(maxsplit=1)[1]
    status = await client.fast_edit(message, f"🎵 **Mencari lagu:** `{query}`...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_DIR}%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Jika bukan URL, cari di YouTube
            if not query.startswith("http"):
                query = f"ytsearch1:{query}"
            
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            
            title = info.get('title', 'audio')
            # Mencari file mp3 yang dihasilkan
            filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + ".mp3"

            if os.path.exists(filename):
                await status.edit("📤 **Mengirim Audio...**")
                await client.send_audio(
                    chat_id=message.chat.id,
                    audio=filename,
                    title=title,
                    performer="Nebula Downloader",
                    caption=f"🎵 **Lagu:** `{title}`"
                )
                await status.delete()
                os.remove(filename)
            else:
                await status.edit("❌ **Gagal mendownload audio.**")

    except Exception as e:
        await status.edit(f"❌ **Error:** `{str(e)}`")
