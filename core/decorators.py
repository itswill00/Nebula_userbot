import functools
import inspect
import os
from hydrogram import filters

# Registry Global
# Format: { 'Category': { 'PluginName': { 'command': 'info' } } }
CMD_HELP = {}

def on_cmd(command, category="General", info="Belum ada info."):
    """
    Dekorator kustom bergaya Ultroid.
    Secara otomatis mendeteksi nama file plugin untuk pengelompokan di Dashboard.
    """
    # Deteksi nama file pemanggil (misal: afk.py -> afk)
    stack = inspect.stack()
    caller_file = stack[1].filename
    plugin_name = os.path.basename(caller_file).replace(".py", "")
    
    if category not in CMD_HELP:
        CMD_HELP[category] = {}
    
    if plugin_name not in CMD_HELP[category]:
        CMD_HELP[category][plugin_name] = {}
        
    CMD_HELP[category][plugin_name][command] = info
    
    return filters.command(command, prefixes=".") & filters.me

# BRAIN_RULES tetap sama
BRAIN_RULES = []

def brain_rule(func):
    BRAIN_RULES.append(func)
    return func
