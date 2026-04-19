import time
import asyncio
from dataclasses import dataclass
from typing import Callable
from hydrogram import Client
from hydrogram.types import Message
from core.decorators import BRAIN_RULES

class Intent:
    # Prioritas Intent (Angka kecil = Prioritas Tinggi)
    BLOCK = 10         # Blokir user
    MUTE = 20          # Mute user
    REPLY_BLOCK = 30   # Balas dengan peringatan blokir
    REPLY = 40         # Balas normal (AFK)
    PASS = 100         # Lewati

@dataclass
class Action:
    intent: int
    plugin_name: str
    execute: Callable

class NebulaBrain:
    def __init__(self, client: Client):
        self.client = client

    async def hydrate_context(self, message: Message) -> dict:
        """Pemuatan Konteks Terpusat. Membaca database SATU KALI untuk semua rule."""
        db = self.client.db
        return {
            "message": message,
            "user_id": message.from_user.id if message.from_user else (message.chat.id if message.chat else None),
            "chat_type": message.chat.type if message.chat else None,
            "time": time.time(),
            # States loaded eagerly
            "afk_data": await db.get("afk", {"is_afk": False}),
            "pm_permit": await db.get("pm_permit_enabled", True),
            "pm_approved": await db.get("pm_approved", []),
            "antispam": await db.get("antispam", False)
        }

    async def process_message(self, client: Client, message: Message):
        # Abaikan pesan dari diri sendiri (dikirim oleh userbot)
        if not message.from_user or message.from_user.is_self:
            return
            
        ctx = await self.hydrate_context(message)
        actions = []

        # Kumpulkan 'Niat' dari semua plugin yang terdaftar di The Brain
        for rule in BRAIN_RULES:
            try:
                action = await rule(self.client, ctx)
                if action:
                    actions.append(action)
            except Exception as e:
                import logging
                logging.error(f"Brain Rule Error ({rule.__name__}): {e}")

        if not actions:
            return

        # Arbitrase: Urutkan aksi berdasarkan prioritas
        actions.sort(key=lambda x: x.intent)
        
        # Eksekusi aksi dengan prioritas tertinggi (hanya satu yang dieksekusi jika terjadi konflik mematikan)
        top_action = actions[0]
        
        await top_action.execute()
        
        # Jika tindakan membatasi alur komunikasi, hentikan propagasi (jangan trigger plugin lain)
        if top_action.intent in (Intent.BLOCK, Intent.MUTE, Intent.REPLY_BLOCK):
            message.stop_propagation()
