import functools
from hydrogram import filters

# Registry Global untuk menyimpan info perintah
CMD_HELP = {}

# Registry Global untuk The Brain (Arbiter System)
BRAIN_RULES = []

def on_cmd(command, category="General", info="Belum ada info."):
    """
    Dekorator kustom untuk mendaftarkan perintah dan bantuan secara otomatis.
    """
    if category not in CMD_HELP:
        CMD_HELP[category] = {}
    
    CMD_HELP[category][command] = info
    
    return filters.command(command, prefixes=".") & filters.me

def brain_rule(func):
    """
    Dekorator untuk mendaftarkan rule pasif ke dalam The Brain (Arbiter System).
    Fungsi harus menerima (client, context) dan mengembalikan Action atau None.
    """
    BRAIN_RULES.append(func)
    return func

