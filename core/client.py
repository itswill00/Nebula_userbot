import os
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

    async def start(self):
        await super().start()
        logging.info("Nebula Engine is now online with LocalDB.")

    async def stop(self, *args):
        await super().stop()
        logging.info("Nebula Engine gracefully terminated.")
