import os
import sys
import time
import psutil
import platform
import distro
import asyncio
from hydrogram import Client
from hydrogram.types import Message
from core.decorators import on_cmd


async def run_cmd(cmd):
    """Menjalankan perintah shell secara asinkron."""
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode().strip(), stderr.decode().strip()


def get_size(bytes, suffix="B"):
    """Skalasi bytes ke format yang mudah dibaca (e.g 1024 ke 1KB)."""
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


@Client.on_message(on_cmd("sysinfo", category="Sistem", info="Informasi sistem."))
async def sys_info(client, message: Message):
    await client.fast_edit(message, "✦ Memproses data...")
    
    # OS Info
    uname = platform.uname()
    os_name = f"{distro.name()} {distro.version()}" if platform.system() == "Linux" else platform.system()
    
    # CPU Info
    cpufreq = psutil.cpu_freq()
    cpu_usage = psutil.cpu_percent()
    
    # Memory Info
    svmem = psutil.virtual_memory()
    
    # Disk Info
    partitions = psutil.disk_partitions()
    disk_info = ""
    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            if partition.mountpoint == "/":
                disk_info = f"{get_size(partition_usage.used)} / {get_size(partition_usage.total)} ({partition_usage.percent}%)"
                break
        except Exception:
            continue

    # Uptime
    uptime_seconds = time.time() - psutil.boot_time()
    uptime_h = int(uptime_seconds // 3600)
    uptime_m = int((uptime_seconds % 3600) // 60)
    
    # Bot Uptime
    bot_uptime_seconds = time.time() - client.start_time
    bot_uptime_h = int(bot_uptime_seconds // 3600)
    bot_uptime_m = int((bot_uptime_seconds % 3600) // 60)

    info = (
        "**Info Sistem**\n\n"
        f"OS     : `{os_name}`\n"
        f"Kernel : `{uname.release}`\n"
        f"Uptime Bot  : `{bot_uptime_h}h {bot_uptime_m}m`\n"
        f"Uptime Host : `{uptime_h}h {uptime_m}m`\n\n"
        f"CPU    : `{cpu_usage}%`\n"
        f"RAM    : `{get_size(svmem.used)} / {get_size(svmem.total)}`\n"
        f"Disk   : `{disk_info}`\n"
    )
    
    await client.fast_edit(message, info)


@Client.on_message(on_cmd("restart", category="Sistem", info="Restart bot."))
async def restart_bot(client, message: Message):
    msg = await client.fast_edit(message, "✦ Sedang merestart...")

    # Simpan konteks untuk pemulihan post-restart (Termasuk Timestamp Downtime)
    await client.db.set("restart_info", {
        "chat_id": message.chat.id,
        "msg_id": msg.id,
        "time": time.time()
    })

    # Eksekusi restart proses (Robust pattern via sys.argv)
    print("🔄 Restarting Nebula...")
    os.execl(sys.executable, sys.executable, *sys.argv)


@Client.on_message(on_cmd("update", category="Sistem", info="Update bot."))
async def update_bot(client, message: Message):
    msg = await client.fast_edit(message, "✦ Mengecek pembaruan...")

    # Ambil perubahan terbaru dari remote
    await run_cmd("wsl git fetch origin main")

    # Cek jumlah komit baru
    out, _ = await run_cmd("wsl git rev-list --count HEAD..origin/main")

    try:
        count = int(out) if out else 0
    except ValueError:
        count = 0

    if count == 0:
        return await msg.edit("Nebula sudah versi terbaru.")

    # Ambil daftar perubahan (changelog)
    changelog, _ = await run_cmd("wsl git log HEAD..origin/main --oneline")

    update_text = (
        f"⬆️ **Ditemukan {count} pembaruan baru!**\n\n"
        f"**Changelog:**\n`{changelog}`\n\n"
        f"⚙️ **Sedang memperbarui...**"
    )
    await msg.edit(update_text)

    # Lakukan Pull
    pull_out, pull_err = await run_cmd("wsl git pull origin main")

    if pull_err and "error" in pull_err.lower():
        return await msg.edit(f"❌ **Gagal memperbarui:**\n`{pull_err}`")

    await msg.edit(f"✦ Pembaruan selesai.\n`{pull_out}`\n\nSedang merestart...")

    # Simpan status untuk pemulihan pasca restart (Termasuk Timestamp Downtime)
    await client.db.set("restart_info", {
        "chat_id": message.chat.id,
        "msg_id": msg.id,
        "time": time.time()
    })

    # Restart (Robust pattern via sys.argv)
    os.execl(sys.executable, sys.executable, *sys.argv)
