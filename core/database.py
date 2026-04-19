import os
import json
import asyncio
import aiofiles

class LocalDB:
    def __init__(self, filename="nebula_db.json"):
        self.filename = filename
        self.lock = asyncio.Lock()
        self._data = {}

    async def _load(self):
        """Memuat data dari file ke memori (private)."""
        if not os.path.exists(self.filename):
            async with aiofiles.open(self.filename, mode='w') as f:
                await f.write(json.dumps({}))
            return {}
        
        async with aiofiles.open(self.filename, mode='r') as f:
            content = await f.read()
            return json.loads(content)

    async def get(self, key, default=None):
        """Membaca data berdasarkan key."""
        async with self.lock:
            data = await self._load()
            return data.get(str(key), default)

    async def set(self, key, value):
        """Menyimpan data (key: value) dan langsung mensinkronisasi ke file."""
        async with self.lock:
            data = await self._load()
            data[str(key)] = value
            async with aiofiles.open(self.filename, mode='w') as f:
                await f.write(json.dumps(data, indent=4))
            return True

    async def delete(self, key):
        """Menghapus key dari database."""
        async with self.lock:
            data = await self._load()
            if str(key) in data:
                del data[str(key)]
                async with aiofiles.open(self.filename, mode='w') as f:
                    await f.write(json.dumps(data, indent=4))
                return True
            return False
