import inspect
import os
from hydrogram import filters

# Registry Global
# Format: { 'Category': { 'PluginName': { 'command': 'info' } } }
CMD_HELP = {}


async def _sudo_filter(_, client, message):
    """Filter dinamis untuk memeriksa izin Sudo."""
    if not message.from_user:
        return False
    # Selalu izinkan pemilik (akun utama)
    if message.from_user.is_self:
        return True
    
    # Periksa daftar sudo di database
    sudo_users = await client.db.get("sudo_users", [])
    return message.from_user.id in sudo_users


# Buat filter resmi Hydrogram
sudo_filter = filters.create(_sudo_filter)


def on_cmd(command, category="General", info="Belum ada info."):
    """
    Dekorator kustom bergaya Ultroid.
    Mendukung Sudo: Perintah bisa dijalankan oleh pemilik ATAU user penyelia (sudo).
    """
    stack = inspect.stack()
    caller_file = stack[1].filename
    plugin_name = os.path.basename(caller_file).replace(".py", "")

    if category not in CMD_HELP:
        CMD_HELP[category] = {}

    if plugin_name not in CMD_HELP[category]:
        CMD_HELP[category][plugin_name] = {}

    if isinstance(command, (list, tuple)):
        for cmd in command:
            CMD_HELP[category][plugin_name][cmd] = info
    else:
        CMD_HELP[category][plugin_name][command] = info

    # Gabungkan filter: Command + (Saya ATAU Sudo)
    return filters.command(command, prefixes=".") & (filters.me | sudo_filter)


# BRAIN_RULES tetap sama
BRAIN_RULES = []


def brain_rule(func):
    BRAIN_RULES.append(func)
    return func
