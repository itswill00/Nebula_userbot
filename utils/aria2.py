import aiohttp
import json

class Aria2RPC:
    def __init__(self, url="http://localhost:6800/jsonrpc"):
        self.url = url

    async def call(self, method, params=None):
        payload = {
            "jsonrpc": "2.0",
            "id": "nebula",
            "method": f"aria2.{method}",
            "params": params or []
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=payload) as resp:
                result = await resp.json()
                if "error" in result:
                    raise Exception(result["error"]["message"])
                return result["result"]

    async def add_url(self, url, output_dir="downloads/"):
        return await self.call("addUri", [[url], {"dir": output_dir}])

    async def get_status(self, gid):
        return await self.call("tellStatus", [gid])

    async def tell_active(self):
        return await self.call("tellActive")
