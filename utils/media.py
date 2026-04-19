import os
import asyncio
import aiohttp
import yt_dlp
from utils.shell import async_exec


async def catbox_upload(file_path):
    """Upload a file to Catbox and return the URL."""
    if not os.path.exists(file_path):
        return None

    url = "https://catbox.moe/user/api.php"
    async with aiohttp.ClientSession() as session:
        with open(file_path, "rb") as f:
            data = aiohttp.FormData()
            data.add_field("reqtype", "fileupload")
            data.add_field("fileToUpload", f, filename=os.path.basename(file_path))

            async with session.post(url, data=data) as response:
                if response.status == 200:
                    return await response.text()
    return None


async def video_to_sticker(input_file: str, output_file: str):
    """Konversi video ke format WebM (VP9) sesuai standar Sticker Telegram."""
    # Scale 512x512, Remove Audio, VP9 Codec, Max 3 seconds
    cmd = (
        f"ffmpeg -i '{input_file}' -t 3 -vf 'scale=512:512:force_original_aspect_ratio=decrease,"
        f"pad=512:512:(ow-iw)/2:(oh-ih)/2:color=#00000000' -an "
        f"-c:v libvpx-vp9 -b:v 256k -pix_fmt yuva420p '{output_file}' -y"
    )
    return await async_exec(cmd)


async def ytdl_download(url: str, output_dir: str):
    """Download media dari 1000+ situs menggunakan yt-dlp."""
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    loop = asyncio.get_event_loop()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
        return ydl.prepare_filename(info)
