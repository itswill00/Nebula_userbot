import os
import json
import time
import logging
import asyncio
from hydrogram import Client, filters
from hydrogram.types import Message
from hydrogram.handlers import MessageHandler
from dotenv import load_dotenv
from core.database import LocalDB
from core.decorators import CMD_HELP
from core.brain import NebulaBrain
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(ROOT_DIR, "nebula.log")),
        logging.StreamHandler()
    ]
)
LOGS = logging.getLogger("Nebula")

# Tetap saring log library internal agar tidak terlalu spammy
logging.getLogger("hydrogram").setLevel(logging.ERROR)
logging.getLogger("apscheduler").setLevel(logging.ERROR)


class NebulaBot(Client):
    def __init__(self):
        # Tampilkan Banner dengan warna biru
        print("\033[94m" + r"""
    _   __     __            __
   / | / /__  / /_  __  ____/ /___ _
  /  |/ / _ \/ __ \/ / / / __  / __ `/
 / /|  /  __/ /_/ / /_/ / /_/ / /_/ /
/_/ |_/\___/_.___/\__,_/\__,_/\__,_/
        """ + "\033[0m")
        LOGS.info("🚀 Inisialisasi Nebula Engine...")

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
        # Load database ke memori agar respon tombol secepat kilat (0ms delay)
        asyncio.get_event_loop().run_until_complete(self.db.load_to_memory())

        self.strings = {}
        self.cmd_help = CMD_HELP
        self.scheduler = AsyncIOScheduler()
        self.start_time = time.time()

        # Inisialisasi The Brain (Arbiter System)
        self.brain = NebulaBrain(self)
        # Register The Brain at group -1 (Tertinggi) untuk mencegat semua pesan
        self.add_handler(MessageHandler(
            self.brain.process_message, filters.all & ~filters.me), group=-1)

        self._load_all_strings()

        # Log Channel Configuration
        log_id = os.getenv("LOG_CHANNEL")
        self.log_channel = int(log_id) if log_id and (
            log_id.startswith("-100") or log_id.isdigit()) else "me"

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
        if not os.path.exists(string_path):
            return
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
        # Jalankan Assistant Bot Terlebih Dahulu (Penting agar .help tidak error saat startup)
        if self.assistant:
            await self.assistant.start()
            # Cache informasi asisten di bot utama agar akses lebih cepat
            self.assistant.me = await self.assistant.get_me()

        await super().start()
        if not self.scheduler.running:
            self.scheduler.start()

        # Kirim notifikasi bot hidup
        await self.send_log("🚀 **Nebula Engine v1.6.0 is Online!**\nAll systems functional.")
        LOGS.info("Nebula Engine 1.6.0 Active.")

    async def stop(self, *args):
        await super().stop()
        if self.scheduler.running:
            self.scheduler.shutdown()
        if self.assistant:
            await self.assistant.stop()
