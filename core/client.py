import os
import json
import logging
import importlib
import asyncio
from hydrogram import Client, filters
from hydrogram.types import Message
from dotenv import load_dotenv
from core.database import LocalDB
from core.decorators import CMD_HELP
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(ROOT_DIR, "nebula.log")),
        logging.StreamHandler()
    ]
)
LOGS = logging.getLogger("Nebula")

class NebulaBot(Client):
    def __init__(self):
        for folder in ["downloads", "strings", "plugins"]:
            target = os.path.join(ROOT_DIR, folder)
            if not os.path.exists(target):
                os.makedirs(target)

        super().__init__(
            name="nebula",
            api_id=int(os.getenv("API_ID")),
            api_hash=os.getenv("API_HASH"),
            plugins=dict(root="plugins"),
            workdir=ROOT_DIR,
            device_model="Nebula Master",
            app_version="1.6.0"
        )
        self.db = LocalDB(os.path.join(ROOT_DIR, "nebula_db.json"))
        self.strings = {}
        self.cmd_help = CMD_HELP
        self.scheduler = AsyncIOScheduler()
        self.start_time = time.time()
        self._load_all_strings()
        
        # Log Channel Configuration
        log_id = os.getenv("LOG_CHANNEL")
        self.log_channel = int(log_id) if log_id and (log_id.startswith("-100") or log_id.isdigit()) else "me"
        
        self.assistant = None
        bot_token = os.getenv("BOT_TOKEN")
        if bot_token:
            self.assistant = Client(
                name="nebula_assistant",
                api_id=int(os.getenv("API_ID")),
                api_hash=os.getenv("API_HASH"),
                bot_token=bot_token,
                workdir=ROOT_DIR,
                no_updates=False
            )
            self.assistant.parent = self

    def _load_all_strings(self):
        string_path = os.path.join(ROOT_DIR, "strings")
        if not os.path.exists(string_path): return
        for lang_file in os.listdir(string_path):
            if lang_file.endswith(".json"):
                lang_code = lang_file.split(".")[0]
                with open(os.path.join(string_path, lang_file), "r", encoding="utf-8") as f:
                    self.strings[lang_code] = json.load(f)

    async def get_string(self, key, default=None):
        lang = await self.db.get("lang", "id")
        return self.strings.get(lang, self.strings.get("id", {})).get(key, default or key)

    async def send_log(self, text: str):
        """Kirim laporan aktivitas ke LOG_CHANNEL."""
        try:
            await self.send_message(self.log_channel, f"📑 **Nebula Log Report**\n\n{text}")
        except Exception as e:
            LOGS.error(f"Failed to send log: {e}")

    async def fast_edit(self, message: Message, text: str, parse_mode=None):
        try:
            return await message.edit(text, parse_mode=parse_mode)
        except Exception as e:
            LOGS.error(f"Edit failed: {e}")
            return message

    async def start(self):
        await super().start()
        if not self.scheduler.running:
            self.scheduler.start()
        if self.assistant:
            await self.assistant.start()
        
        # Kirim notifikasi bot hidup
        await self.send_log("🚀 **Nebula Engine v1.6.0 is Online!**\nAll systems functional.")
        LOGS.info("Nebula Engine 1.6.0 Active.")

    async def stop(self, *args):
        await super().stop()
        if self.scheduler.running:
            self.scheduler.shutdown()
        if self.assistant:
            await self.assistant.stop()
