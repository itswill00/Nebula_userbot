import os
import json
import asyncio
import aiofiles
import logging

LOGS = logging.getLogger("Nebula.DB")

class LocalDB:
    def __init__(self, filename="nebula_db.json"):
        self.filename = filename
        self.lock = asyncio.Lock()
        self._cache = {}
        self.msg_cache = {} 

    async def load_to_memory(self):
        """Muat seluruh data dari file ke memori saat startup."""
        async with self.lock:
            if not os.path.exists(self.filename):
                self._cache = {}
                await self._save_to_disk()
                return
            
            try:
                async with aiofiles.open(self.filename, mode='r') as f:
                    content = await f.read()
                    self._cache = json.loads(content) if content else {}
                LOGS.info("Database loaded to memory.")
            except Exception as e:
                LOGS.error(f"Failed to load DB: {e}")
                self._cache = {}

    async def _save_to_disk(self):
        """Simpan cache memori ke file secara asinkron."""
        try:
            async with aiofiles.open(self.filename, mode='w') as f:
                await f.write(json.dumps(self._cache, indent=4))
        except Exception as e:
            LOGS.error(f"Failed to save DB to disk: {e}")

    async def get(self, key, default=None):
        """Ambil data langsung dari memori (Sangat Cepat)."""
        return self._cache.get(str(key), default)

    async def set(self, key, value):
        """Update memori dan simpan ke disk di background."""
        async with self.lock:
            self._cache[str(key)] = value
            await self._save_to_disk()
            return True

    async def delete(self, key):
        """Hapus dari memori dan update disk."""
        async with self.lock:
            if str(key) in self._cache:
                del self._cache[str(key)]
                await self._save_to_disk()
                return True
            return False

    async def all_data(self):
        """Mengembalikan salinan semua data di memori."""
        return self._cache.copy()
