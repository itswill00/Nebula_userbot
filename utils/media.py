import aiohttp
import os

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
