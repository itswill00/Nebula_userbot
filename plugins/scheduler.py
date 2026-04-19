import datetime
from hydrogram import Client, filters
from hydrogram.types import Message

PREFIX = "."

async def send_reminder(client, chat_id, text):
    """Fungsi callback yang dijalankan oleh scheduler."""
    await client.send_message(chat_id, f"⏰ **Nebula Reminder:**\n\n`{text}`")

@Client.on_message(filters.command("remind", prefixes=PREFIX) & filters.me)
async def set_reminder(client, message: Message):
    """Menjadwalkan pengingat. Format: .remind <waktu_menit> <teks>"""
    if len(message.command) < 3:
        return await message.edit("`Format: .remind <menit> <teks>`")
    
    try:
        minutes = int(message.command[1])
        text = message.text.split(None, 2)[2]
        
        run_at = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        
        client.scheduler.add_job(
            send_reminder,
            "date",
            run_date=run_at,
            args=[client, message.chat.id, text]
        )
        
        await message.edit(f"✅ `Pengingat diset untuk {minutes} menit dari sekarang.`")
    except Exception as e:
        await message.edit(f"❌ `Error:` `{str(e)}`")

@Client.on_message(filters.command("jobs", prefixes=PREFIX) & filters.me)
async def list_jobs(client, message: Message):
    """Menampilkan daftar tugas yang dijadwalkan."""
    jobs = client.scheduler.get_jobs()
    if not jobs:
        return await message.edit("`Tidak ada tugas yang dijadwalkan.`")
    
    text = "**Nebula Scheduled Jobs:**\n\n"
    for job in jobs:
        text += f"📍 `{job.id}` - `{job.next_run_time}`\n"
    await message.edit(text)
