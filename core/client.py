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
            device_model="Nebula",
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
        self.owner_id = int(
            owner_id) if owner_id and owner_id.isdigit() else None

        self.scheduler = AsyncIOScheduler()
        self.start_time = time.time()
        self._media_cache = {}  # Session Media Cache (Ultroid-tier speed)

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
        self.start_time = time.time()  # Reset start_time to now

        # Auto-detect Owner ID jika tidak diset di env
        if not self.owner_id:
            self.owner_id = self.me.id

        if not self.scheduler.running:
            self.scheduler.start()

        # Pemulihan pasca restart
        restart_data = await self.db.get("restart_info")
        is_restarted = False
        downtime_str = None
        if restart_data:
            chat_id = restart_data.get("chat_id")
            msg_id = restart_data.get("msg_id")
            old_time = restart_data.get("time")

            if old_time:
                dt = time.time() - old_time
                downtime_str = f"{int(dt)}s" if dt < 60 else f"{int(dt/60)}m {int(dt % 60)}s"

            try:
                msg_status = "✅ **Nebula Berhasil Direstart!**"
                if downtime_str:
                    msg_status += f"\n📉 Downtime: `{downtime_str}`"
                await self.edit_message_text(chat_id, msg_id, msg_status)
                is_restarted = True
            except Exception:
                pass
            await self.db.delete("restart_info")

        # Notifikasi Startup (Telemetri DASHBOARD)
        if self.log_channel and self.assistant:
            await self._send_startup_notice(is_restarted, downtime_str)

    @property
    def banner_url(self):
        """Ambil URL atau Path banner (Prioritas Lokal)."""
        # 1. Cek folder lokal (Balanced Visuals)
        banners_dir = os.path.join(ROOT_DIR, "resources", "banners")
        if os.path.exists(banners_dir):
            import random
            banners = [os.path.join(banners_dir, f) for f in os.listdir(banners_dir)
                       if f.lower().endswith((".png", ".jpg", ".jpeg"))]
            if banners:
                return random.choice(banners)

        # 2. Fallback ke Environment Variable
        env_banner = os.getenv("BANNER")
        if env_banner:
            return env_banner

        # 3. Fallback terakhir (standard link)
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

    async def send_log(self, text: str):
        """Kirim laporan aktivitas ke LOG_CHANNEL (Minimalist Style)."""
        if not self.log_channel or not self.assistant:
            return
        try:
            await self.assistant.send_message(
                self.log_channel,
                f"📑 **Nebula Log**\n\n{text}"
            )
        except Exception as e:
            LOGS.error(f"Failed to send log: {e}")

    async def send_card(self, chat_id, text, buttons=None, reply_to_message_id=None):
        """Kirim tampilan dengan banner visual (Bulletproof Engine)."""
        # 1. Cek Session Cache (Ultra Speed)
        if chat_id in self._media_cache:
            try:
                return await self.assistant.send_photo(
                    chat_id,
                    photo=self._media_cache[chat_id],
                    caption=text,
                    reply_markup=buttons,
                    reply_to_message_id=reply_to_message_id
                )
            except Exception:
                del self._media_cache[chat_id]

        # 2. Cek Database Cache
        cached_id = await self.db.get("banner_file_id")

        # Coba Kirim via Cache (Paling Stabil)
        if cached_id:
            try:
                msg = await self.assistant.send_photo(
                    chat_id,
                    photo=cached_id,
                    caption=text,
                    reply_markup=buttons,
                    reply_to_message_id=reply_to_message_id
                )
                self._media_cache[chat_id] = cached_id
                return msg
            except Exception as e:
                LOGS.warning(f"Media Engine Cache Failed: {e}")

        # 2. Ambil Source Banner (Lokal atau URL)
        source = self.banner_url

        # Priority 2: Streaming Lokal atau URL
        try:
            # Jika source adalah path file lokal, kirim sebagai stream biner
            if os.path.exists(str(source)):
                with open(source, "rb") as photo:
                    return await self.assistant.send_photo(
                        chat_id,
                        photo=photo,
                        caption=text,
                        reply_markup=buttons,
                        reply_to_message_id=reply_to_message_id
                    )

            # Jika source adalah URL (Fallback ke Standard Telegraph)
            return await self.assistant.send_photo(
                chat_id,
                photo=source,
                caption=text,
                reply_markup=buttons,
                reply_to_message_id=reply_to_message_id
            )
        except Exception as e:
            LOGS.error(f"Media Engine Critical Failure: {e}")
            # Priority 3: Safe Mode (Teks Murni)
            return await self.assistant.send_message(
                chat_id,
                text,
                reply_markup=buttons,
                reply_to_message_id=reply_to_message_id,
                disable_web_page_preview=True
            )

    async def _send_startup_notice(self, is_restarted, downtime=None):
        """Kirim kartu telemetri startup via Assistant."""
        try:
            # 1. Bersihkan Log Startup Sebelumnya
            old_log_id = await self.db.get("last_startup_log_id")
            if old_log_id:
                try:
                    await self.assistant.delete_messages(self.log_channel, old_log_id)
                except Exception:
                    pass

            # 2. Kumpulkan Metrik Sistem (Ultroid-tier High Density)
            uname = platform.uname()
            os_name = f"{platform.system()}"
            arch = uname.machine
            kernel = uname.release
            py_ver = platform.python_version()
            ram = psutil.virtual_memory().percent

            # Hitung Plugin Aktif
            plugin_list = [f for f in os.listdir(
                "plugins") if f.endswith(".py") and not f.startswith("_")]
            plugin_count = len(plugin_list)

            # 3. Desain Laporan (Zero Gimmick HUD - Enhanced)
            status_text = "DIRESTART" if is_restarted else "AKTIF"
            header_ico = "🔄" if is_restarted else "🚀"

            card_text = (
                f"{header_ico} **Nebula {status_text}**\n"
                f"━━━━━━━━━━━━━━━\n"
                f"Sistem   : {os_name} ({arch})\n"
                f"Kernel   : {kernel}\n"
                f"Engine   : {py_ver} / 1.6.0\n"
                f"Fitur    : {plugin_count} total\n"
                f"Status   : {ram}% Memory Load"
            )
            if downtime:
                card_text += f"\n📉 Downtime : {downtime}"

            # 4. Tombol Fungsional
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "Bantuan", callback_data="back_to_main"),
                    InlineKeyboardButton(
                        "Sistem", callback_data="cat|System|0")
                ]
            ])

            # 5. Kirim Laporan via Media Engine
            msg = await self.send_card(
                self.log_channel,
                card_text,
                buttons=buttons
            )

            # 6. Bulk Caching (Shifting Cosmos - Visual Rebirth)
            banner_ids = []
            if msg and hasattr(msg, "photo") and msg.photo:
                banner_ids.append(msg.photo.file_id)
                await self.db.set("banner_file_id", msg.photo.file_id)

            banners_dir = os.path.join(ROOT_DIR, "resources", "banners")
            if os.path.exists(banners_dir):
                for f in os.listdir(banners_dir):
                    if f.lower().endswith((".png", ".jpg", ".jpeg")):
                        try:
                            # Caching silent
                            m = await self.assistant.send_photo(
                                self.log_channel,
                                photo=os.path.join(banners_dir, f),
                                caption=f"◈ Mencache visual: `{f}`"
                            )
                            if m.photo:
                                banner_ids.append(m.photo.file_id)
                            await m.delete()
                        except Exception:
                            pass

            if banner_ids:
                await self.db.set("banner_file_ids", list(set(banner_ids)))

            if msg:
                await self.db.set("last_startup_log_id", msg.id)

            return msg
        except Exception as e:
            LOGS.error(f"Failed to send startup notice: {e}")

        LOGS.info("Nebula 1.6.0 Active.")

    async def stop(self, *args):
        await super().stop()
        if self.scheduler.running:
            self.scheduler.shutdown()
        if self.assistant:
            await self.assistant.stop()
