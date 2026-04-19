import os
import json
import logging
from hydrogram import Client
from dotenv import load_dotenv
from core.database import LocalDB

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
            app_version="1.0.0"
        )
        self.db = LocalDB()
        self.strings = {}
        self._load_all_strings()
        
        # Inisialisasi Assistant jika BOT_TOKEN tersedia
        self.assistant = None
        bot_token = os.getenv("BOT_TOKEN")
        if bot_token:
            self.assistant = Client(
                name="nebula_assistant",
                api_id=int(os.getenv("API_ID")),
                api_hash=os.getenv("API_HASH"),
                bot_token=bot_token,
                no_updates=False # Assistant butuh updates untuk callback tombol
            )

    def _load_all_strings(self):
        for lang_file in os.listdir("strings"):
            if lang_file.endswith(".json"):
                lang_code = lang_file.split(".")[0]
                with open(f"strings/{lang_file}", "r") as f:
                    self.strings[lang_code] = json.load(f)

    async def get_string(self, key, default=None):
        lang = await self.db.get("lang", "id")
        return self.strings.get(lang, self.strings["id"]).get(key, default or key)

    async def start(self):
        await super().start()
        if self.assistant:
            await self.assistant.start()
            logging.info("Nebula Assistant (Bot) is online.")
        logging.info("Nebula Master (User) is online.")

    async def stop(self, *args):
        await super().stop()
        if self.assistant:
            await self.assistant.stop()
        logging.info("Nebula Engine gracefully terminated.")
