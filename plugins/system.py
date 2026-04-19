import time
import os
import psutil
import platform
from datetime import datetime
from hydrogram import Client, filters
from hydrogram.types import Message
from core.decorators import on_cmd

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["detik", "menit", "jam", "hari"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + " " + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

@Client.on_message(on_cmd("ping", category="System", info="Cek latensi bot."))
async def ping_cmd(client, message: Message):
    start = time.time()
    ex = await client.fast_edit(message, "🏓 **Pinging...**")
    end = time.time()
    duration = round((end - start) * 1000, 2)
    uptime = get_readable_time(time.time() - client.start_time)
    await ex.edit(f"🚀 **Pong!**\n\n⏱️ **Latensi:** `{duration}ms`\n⏳ **Uptime:** `{uptime}`")

@Client.on_message(on_cmd("uptime", category="System", info="Cek berapa lama bot berjalan."))
async def uptime_cmd(client, message: Message):
    uptime = get_readable_time(time.time() - client.start_time)
    await client.fast_edit(message, f"🕒 **Nebula Uptime:** `{uptime}`")

@Client.on_message(on_cmd("sysinfo", category="System", info="Informasi sistem lengkap."))
async def sysinfo_cmd(client, message: Message):
    uname = platform.uname()
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    
    # CPU
    cpufreq = psutil.cpu_freq()
    
    # Memory
    svmem = psutil.virtual_memory()
    
    # Disk
    disk_usage = psutil.disk_usage('/')

    res = (
        "💻 **System Information**\n\n"
        f"**OS:** `{uname.system} {uname.release}`\n"
        f"**Node Name:** `{uname.node}`\n"
        f"**CPU Core:** `{psutil.cpu_count(logical=False)} Cores` / `{psutil.cpu_count(logical=True)} Threads`\n"
        f"**CPU Speed:** `{cpufreq.max:.2f}Mhz`\n"
        f"**Total RAM:** `{get_size(svmem.total)}` (`{svmem.percent}% used`)\n"
        f"**Disk Space:** `{get_size(disk_usage.total)}` (`{disk_usage.percent}% used`)\n"
        f"**Boot Time:** `{bt.day}/{bt.month}/{bt.year} {bt.hour}:{bt.minute}:{bt.second}`"
    )
    await client.fast_edit(message, res)

@Client.on_message(on_cmd("usage", category="System", info="Penggunaan sumber daya saat ini."))
async def usage_cmd(client, message: Message):
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    
    res = (
        "📊 **Current Resource Usage**\n\n"
        f"**CPU:** `{cpu_usage}%`\n"
        f"**RAM:** `{ram_usage}%`\n"
        f"**Disk:** `{disk_usage}%`"
    )
    await client.fast_edit(message, res)
