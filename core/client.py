import os
import json
import logging
import importlib
import asyncio
from hydrogram import Client, filters
from hydrogram.types import Message
from dotenv import load_dotenv
from core.database import LocalDB
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Konfigurasi Logging Pro
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
    """
    NebulaClient yang terinspirasi dari Ultroid.
    Menambahkan fungsionalitas bantuan langsung ke dalam objek Client.
    """
    def __init__(self):
        # Inisialisasi direktori
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
            app_version="1.4.0"
        )
        self.db = LocalDB(os.path.join(ROOT_DIR, "nebula_db.json"))
        self.strings = {}
        self.cmd_help = {} # Registry untuk menyimpan info perintah
        self.scheduler = AsyncIOScheduler()
        self._load_all_strings()
        
        # Dual-Client Logic
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
            # Shortcut untuk parent access
            self.assistant.parent = self

    def _load_all_strings(self):
        string_path = os.path.join(ROOT_DIR, "strings")
        for lang_file in os.listdir(string_path):
            if lang_file.endswith(".json"):
                lang_code = lang_file.split(".")[0]
                with open(os.path.join(string_path, lang_file), "r", encoding="utf-8") as f:
                    self.strings[lang_code] = json.load(f)

    async def get_string(self, key, default=None):
        lang = await self.db.get("lang", "id")
        return self.strings.get(lang, self.strings.get("id", {})).get(key, default or key)

    # --- HELPER METHODS (Ultroid Style) ---
    
    async def fast_edit(self, message: Message, text: str, parse_mode=None):
        """Edit pesan dengan penanganan error yang lebih baik."""
        try:
            return await message.edit(text, parse_mode=parse_mode)
        except Exception as e:
            LOGS.error(f"Edit failed: {e}")
            return message

    async def run_in_loop(self, coroutine):
        """Menjalankan coroutine dalam event loop bot."""
        return asyncio.get_event_loop().create_task(coroutine)

    async def start(self):
        await super().start()
        if not self.scheduler.running:
            self.scheduler.start()
        if self.assistant:
            await self.assistant.start()
            LOGS.info("Assistant Online.")
        LOGS.info("Nebula Engine 1.4.0 (Modular) is now running.")

    async def stop(self, *args):
        await super().stop()
        if self.scheduler.running:
            self.scheduler.shutdown()
        if self.assistant:
            await self.assistant.stop()
