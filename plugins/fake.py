import asyncio
from hydrogram import Client
from hydrogram.types import Message
from hydrogram.enums import ChatAction
from core.decorators import on_cmd

@Client.on_message(on_cmd("ftype", category="Fun", info="Status pura-pura ngetik."))
async def fake_typing(client, message: Message):
    await message.delete()
    
    try:
        # Kirim status mengetik selama 30 detik (Telegram membatasi action)
        for _ in range(6): 
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            await asyncio.sleep(5)
    except Exception:
        pass

@Client.on_message(on_cmd("fvoice", category="Fun", info="Status pura-pura merekam voice note."))
async def fake_voice(client, message: Message):
    await message.delete()
    
    try:
        for _ in range(6):
            await client.send_chat_action(message.chat.id, ChatAction.RECORD_AUDIO)
            await asyncio.sleep(5)
    except Exception:
        pass

@Client.on_message(on_cmd("fvideo", category="Fun", info="Status pura-pura merekam video."))
async def fake_video(client, message: Message):
    await message.delete()
    
    try:
        for _ in range(6):
            await client.send_chat_action(message.chat.id, ChatAction.RECORD_VIDEO)
            await asyncio.sleep(5)
    except Exception:
        pass
