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
            api_id=int(os.getenv("API_ID", 12345)),
            api_hash=os.getenv("API_HASH", "replace_me"),
            plugins=dict(root="plugins"),
            device_model="Nebula VPS Engine",
            system_version="Linux Container",
            app_version="1.0.0"
        )
        self.db = LocalDB()
        self.strings = {}
        self._load_all_strings()

    def _load_all_strings(self):
        """Memuat seluruh file bahasa ke memori saat startup (efisiensi)."""
        for lang_file in os.listdir("strings"):
            if lang_file.endswith(".json"):
                lang_code = lang_file.split(".")[0]
                with open(f"strings/{lang_file}", "r") as f:
                    self.strings[lang_code] = json.load(f)

    async def get_string(self, key, default=None):
        """Mengambil teks terjemahan berdasarkan preferensi user."""
        lang = await self.db.get("lang", "id")
        return self.strings.get(lang, self.strings["id"]).get(key, default or key)

    async def start(self):
        await super().start()
        logging.info("Nebula Engine is online with Dynamic Config & i18n.")

    async def stop(self, *args):
        await super().stop()
        logging.info("Nebula Engine gracefully terminated.")
