import os
import json
import asyncio
import aiofiles
from collections import deque

class LocalDB:
    def __init__(self, filename="nebula_db.json"):
        self.filename = filename
        self.lock = asyncio.Lock()
        self.msg_cache = {} # In-memory cache for Anti-Delete (key: msg_id, val: msg_obj)

    async def _load(self):
        if not os.path.exists(self.filename):
            async with aiofiles.open(self.filename, mode='w') as f:
                await f.write(json.dumps({}))
            return {}
        async with aiofiles.open(self.filename, mode='r') as f:
            content = await f.read()
            return json.loads(content)

    async def get(self, key, default=None):
        async with self.lock:
            data = await self._load()
            return data.get(str(key), default)

    async def set(self, key, value):
        async with self.lock:
            data = await self._load()
            data[str(key)] = value
            async with aiofiles.open(self.filename, mode='w') as f:
                await f.write(json.dumps(data, indent=4))
            return True

    async def delete(self, key):
        async with self.lock:
            data = await self._load()
            if str(key) in data:
                del data[str(key)]
                async with aiofiles.open(self.filename, mode='w') as f:
                    await f.write(json.dumps(data, indent=4))
                return True
            return False
