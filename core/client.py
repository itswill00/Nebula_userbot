import os
import json
import logging
import importlib
from hydrogram import Client
from dotenv import load_dotenv
from core.database import LocalDB
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NebulaBot(Client):
    def __init__(self):
        super().__init__(
            name="nebula",
            api_id=int(os.getenv("API_ID")),
            api_hash=os.getenv("API_HASH"),
            plugins=dict(root="plugins"),
            device_model="Nebula Master",
            app_version="1.2.0"
        )
        self.db = LocalDB()
        self.strings = {}
        self.scheduler = AsyncIOScheduler()
        self._load_all_strings()
        
        self.assistant = None
        bot_token = os.getenv("BOT_TOKEN")
        if bot_token:
            self.assistant = Client(
                name="nebula_assistant",
                api_id=int(os.getenv("API_ID")),
                api_hash=os.getenv("API_HASH"),
                bot_token=bot_token,
                no_updates=False
            )

    def _load_all_strings(self):
        if not os.path.exists("strings"):
            os.makedirs("strings")
        for lang_file in os.listdir("strings"):
            if lang_file.endswith(".json"):
                lang_code = lang_file.split(".")[0]
                with open(f"strings/{lang_file}", "r") as f:
                    self.strings[lang_code] = json.load(f)

    async def get_string(self, key, default=None):
        lang = await self.db.get("lang", "id")
        return self.strings.get(lang, self.strings.get("id", {})).get(key, default or key)

    async def reload_plugin(self, name):
        module_path = f"plugins.{name}"
        try:
            module = importlib.import_module(module_path)
            importlib.reload(module)
            return True
        except Exception as e:
            logging.error(f"Error reloading {name}: {e}")
            return False

    async def start(self):
        await super().start()
        self.scheduler.start()
        if self.assistant:
            await self.assistant.start()
            logging.info("Assistant Online.")
        logging.info("Nebula Core Online with Scheduler Active.")

    async def stop(self, *args):
        await super().stop()
        self.scheduler.shutdown()
        if self.assistant:
            await self.assistant.stop()
