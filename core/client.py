import os
import json
import time
import logging
import asyncio
import platform
import psutil
from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
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
        LOGS.info("🚀 Inisialisasi Nebula...")

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
        self.current_lang = "id"
        self._load_strings()
        # Load database ke memori agar respon tombol secepat kilat (0ms delay)
        asyncio.get_event_loop().run_until_complete(self.db.load_to_memory())

        # Konfigurasi ID Pemilik
        owner_id = os.getenv("OWNER_ID")
        self.owner_id = int(owner_id) if owner_id and owner_id.isdigit() else None

        self.scheduler = AsyncIOScheduler()
        self.start_time = time.time()

        # Inisialisasi The Brain (Arbiter System)
        self.brain = NebulaBrain(self)
        # Register The Brain at group -1 (Tertinggi) untuk mencegat semua pesan
        self.add_handler(MessageHandler(
            self.brain.process_message, filters.all & ~filters.me), group=-1)

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

    async def fast_edit(self, message: Message, text: str, **kwargs):
        try:
            return await message.edit(text, **kwargs)
        except Exception as e:
            LOGS.error(f"Edit failed: {e}")
            return message

    async def start(self):
        # Jalankan Assistant Bot Terlebih Dahulu
        if self.assistant:
            await self.assistant.start()
            self.assistant.me = await self.assistant.get_me()

        await super().start()
        
        # Auto-detect Owner ID jika tidak diset di env
        if not self.owner_id:
            self.owner_id = self.me.id
            
        if not self.scheduler.running:
            self.scheduler.start()

        # Pemulihan pasca restart
        restart_data = await self.db.get("restart_info")
        is_restarted = False
        if restart_data:
            chat_id = restart_data.get("chat_id")
            msg_id = restart_data.get("msg_id")
            try:
                await self.edit_message_text(chat_id, msg_id, "✅ **Nebula Berhasil Direstart!**")
                is_restarted = True
            except Exception:
                pass
            await self.db.delete("restart_info")

        # Notifikasi Startup (Telemetri DASHBOARD)
        if self.log_channel and self.assistant:
            await self._send_startup_notice(is_restarted)

    @property
    def banner_url(self):
        """Ambil URL banner dari env atau gunakan default lokal."""
        env_banner = os.getenv("BANNER")
        if env_banner:
            return env_banner
        # Fallback ke banner lokal jika ada
        local_path = os.path.join(ROOT_DIR, "resources", "banner.png")
        if os.path.exists(local_path):
            return local_path
        # Default fallback (Direct High-Speed Link)
        return "https://telegra.ph/file/0c976939988a8f6022ced.jpg"

    def _load_strings(self):
        """Muat semua file modul bahasa ke memori (Localization System)."""
        strings_dir = os.path.join(ROOT_DIR, "resources", "strings")
        if not os.path.exists(strings_dir):
            return
        
        for lang_file in os.listdir(strings_dir):
            if lang_file.endswith(".json"):
                lang_code = lang_file.replace(".json", "")
                try:
                    with open(os.path.join(strings_dir, lang_file), "r", encoding="utf-8") as f:
                        self.strings[lang_code] = json.load(f)
                except Exception as e:
                    LOGS.error(f"Gagal memuat bahasa {lang_file}: {e}")

    def get_string(self, key: str) -> str:
        """Ambil teks berdasarkan bahasa aktif (Fallback ke EN jika ID tidak ada)."""
        lang = self.current_lang
        # Prioritas: Bahasa Aktif -> Bahasa Inggris -> Key itu sendiri
        return self.strings.get(lang, {}).get(key, 
               self.strings.get("en", {}).get(key, key))

    async def send_card(self, chat_id, text, buttons=None, reply_to_message_id=None):
        """Kirim pesan dengan banner & tombol bergaya premium (Graceful Fallback)."""
        try:
            # Kirim via asisten agar identitas bot tetap profesional
            client = self.assistant if self.assistant else self
            return await client.send_photo(
                chat_id,
                photo=self.banner_url,
                caption=text,
                reply_markup=buttons,
                reply_to_message_id=reply_to_message_id
            )
        except Exception as e:
            LOGS.warning(f"Media Engine fallback: {e}")
            # Fallback ke teks murni jika media bermasalah (Ultroid Style)
            return await self.send_message(
                chat_id,
                text,
                reply_markup=buttons,
                reply_to_message_id=reply_to_message_id,
                disable_web_page_preview=True
            )

    async def _send_startup_notice(self, is_restarted):
        """Kirim kartu telemetri startup via Assistant."""
        try:
            # 1. Bersihkan Log Startup Sebelumnya
            old_log_id = await self.db.get("last_startup_log_id")
            if old_log_id:
                try:
                    await self.assistant.delete_messages(self.log_channel, old_log_id)
                except Exception:
                    pass

            # 2. Kumpulkan Metrik Sistem
            os_name = platform.system()
            arch = platform.machine()
            py_ver = platform.python_version()
            ram = psutil.virtual_memory().percent
            
            # Hitung Plugin Aktif
            plugin_list = [f for f in os.listdir("plugins") if f.endswith(".py") and not f.startswith("_")]
            plugin_count = len(plugin_list)

            # 3. Desain Kartu (Premium Style)
            status_emoji = "🔄" if is_restarted else "🚀"
            status_text = "Nebula Restarted" if is_restarted else "Nebula Online"
            
            card_text = (
                f"{status_emoji} **{status_text}**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **Owner:** {self.me.mention}\n"
                f"🤖 **Assistant:** {self.assistant.me.mention}\n\n"
                f"🖥️ **System:** `{os_name}` ({arch})\n"
                f"⚙️ **Engine:** `Python {py_ver}`\n"
                f"🧩 **Plugins:** `{plugin_count}` Active\n"
                f"🧠 **RAM Load:** `{ram}%`"
            )

            # 4. Tombol Interaktif
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🛠️ Dashboard", callback_data="back_to_main"),
                    InlineKeyboardButton("📊 Stats", callback_data="cat|System|0")
                ],
                [
                    InlineKeyboardButton("🌐 Repository", url="https://github.com/itswill00/Nebula_userbot")
                ]
            ])

            # 5. Kirim menggunakan Media Engine
            msg = await self.send_card(
                self.log_channel,
                card_text,
                buttons=buttons
            )
            
            # Simpan ID untuk pembersihan berikutnya
            if msg:
                await self.db.set("last_startup_log_id", msg.id)
                
        except Exception as e:
            LOGS.error(f"Failed to send startup notice: {e}")

        LOGS.info("Nebula 1.6.0 Active.")

    async def stop(self, *args):
        await super().stop()
        if self.scheduler.running:
            self.scheduler.shutdown()
        if self.assistant:
            await self.assistant.stop()
